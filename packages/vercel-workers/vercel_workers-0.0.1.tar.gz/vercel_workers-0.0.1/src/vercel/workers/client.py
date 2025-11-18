from __future__ import annotations

import asyncio
import json
import sys
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Protocol, TypedDict

__all__ = [
    "MessageMetadata",
    "WorkerTimeoutResult",
    "subscribe",
    "wsgi_app",
    "has_subscriptions",
]


class MessageMetadata(TypedDict, total=False):
    """Metadata describing a queue message delivery."""

    messageId: str
    deliveryCount: int
    createdAt: str
    topic: str
    consumer: str


class WorkerTimeoutResult(TypedDict):
    """Result that instructs the queue to retry the message later."""

    timeoutSeconds: int


class WorkerCallable(Protocol):
    def __call__(self, message: Any, metadata: MessageMetadata) -> Any | Awaitable[Any]: ...


@dataclass
class _Subscription:
    func: WorkerCallable
    topic: str | None = None
    consumer: str | None = None


_subscriptions: list[_Subscription] = []


def subscribe(
    _func: WorkerCallable | None = None,
    *,
    topic: str | None = None,
    consumer: str | None = None,
) -> Callable[[WorkerCallable], WorkerCallable] | WorkerCallable:
    """
    Register a queue worker function.

    Usage:

        @subscribe
        def worker(message, metadata): ...

        @subscribe(topic="events", consumer="billing")
        def billing_worker(message, metadata): ...
    """

    def decorator(func: WorkerCallable) -> WorkerCallable:
        _subscriptions.append(_Subscription(func=func, topic=topic, consumer=consumer))

        @wraps(func)
        def wrapper(message: Any, metadata: MessageMetadata) -> Any:
            return func(message, metadata)

        return wrapper  # type: ignore[return-value]

    if _func is not None:
        # Used as @subscribe without arguments
        return decorator(_func)

    # Used as @subscribe(...)
    return decorator


def has_subscriptions() -> bool:
    """Return True if any worker functions have been registered via @subscribe."""
    return bool(_subscriptions)


def _get_header(environ: dict[str, Any], name: str) -> str | None:
    """
    Look up a HTTP header from the WSGI environ by its canonical name.

    Example: name="Vqs-Queue-Name" -> environ["HTTP_VQS_QUEUE_NAME"].
    """
    key = "HTTP_" + name.upper().replace("-", "_")
    value = environ.get(key)
    if value is None:
        return None
    # WSGI may give bytes in some servers
    if isinstance(value, bytes):
        return value.decode("latin1")
    return str(value)


def _parse_metadata(environ: dict[str, Any]) -> MessageMetadata:
    """
    Derive MessageMetadata from queue-related headers when available.

    This mirrors the JS client header names where possible:
      - Vqs-Message-Id
      - Vqs-Delivery-Count
      - Vqs-Timestamp
      - Vqs-Queue-Name  (used as topic)
      - Vqs-Consumer-Group (used as consumer)
    """
    message_id = _get_header(environ, "Vqs-Message-Id")
    delivery_count_raw = _get_header(environ, "Vqs-Delivery-Count") or "0"
    timestamp = _get_header(environ, "Vqs-Timestamp")
    topic = _get_header(environ, "Vqs-Queue-Name")
    consumer = _get_header(environ, "Vqs-Consumer-Group")

    try:
        delivery_count = int(delivery_count_raw)
    except ValueError:
        delivery_count = 0

    meta: MessageMetadata = {}
    if message_id is not None:
        meta["messageId"] = message_id
    meta["deliveryCount"] = delivery_count
    if timestamp is not None:
        meta["createdAt"] = timestamp
    if topic is not None:
        meta["topic"] = topic
    if consumer is not None:
        meta["consumer"] = consumer
    return meta


def _read_body(environ: dict[str, Any]) -> bytes:
    try:
        length = int(environ.get("CONTENT_LENGTH") or "0")
    except ValueError:
        length = 0
    wsgi_input = environ.get("wsgi.input")
    if not wsgi_input or length <= 0:
        return b""
    return wsgi_input.read(length)


def _select_subscriptions(
    topic: str | None,
    consumer: str | None,
) -> Iterable[_Subscription]:
    # First try to match explicitly on topic and consumer if any subscriptions
    # declare them. If none match, fall back to all subscriptions.
    explicit_matches = [
        s
        for s in _subscriptions
        if (s.topic is None or s.topic == topic)
        and (s.consumer is None or s.consumer == consumer)
    ]
    if explicit_matches:
        return explicit_matches
    return list(_subscriptions)


def _invoke_subscriptions(message: Any, metadata: MessageMetadata) -> int | None:
    """
    Invoke all matching subscriptions and return an optional timeoutSeconds.

    If a worker returns a dict like {"timeoutSeconds": 300} then that value
    will be propagated back to the queue service to delay the next attempt.
    """
    topic = metadata.get("topic")
    consumer = metadata.get("consumer")
    timeout_seconds: int | None = None

    for sub in _select_subscriptions(topic, consumer):
        try:
            result = sub.func(message, metadata)
            if asyncio.iscoroutine(result) or isinstance(result, asyncio.Future):
                result = asyncio.run(result)  # type: ignore[arg-type]
        except Exception:
            # Let the outer WSGI handler respond with 500.
            raise

        if isinstance(result, dict) and "timeoutSeconds" in result:
            try:
                timeout_seconds = int(result["timeoutSeconds"])
            except (TypeError, ValueError):
                # Ignore invalid timeout values; continue with previous one if any.
                pass

    return timeout_seconds


def wsgi_app(environ: dict[str, Any], start_response: Callable[..., Any]):
    """
    Minimal WSGI application that dispatches queue messages to subscribed workers.

    Expected request:
      - HTTP headers contain queue metadata (Vqs-* headers).
      - Body is JSON, either:
          { "message": <payload>, "metadata": {...} }
        or:
          <payload>
    """
    if not _subscriptions:
        body = b'{"error":"no-subscribers"}'
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "application/json"), ("Content-Length", str(len(body)))],
        )
        return [body]

    try:
        raw = _read_body(environ)
        message: Any
        metadata = _parse_metadata(environ)

        if raw:
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                # If body is not valid JSON, treat raw bytes as message
                message = raw
            else:
                if isinstance(data, dict) and "message" in data:
                    message = data.get("message")
                    extra_meta = data.get("metadata") or {}
                    if isinstance(extra_meta, dict):
                        # Shallow merge: body metadata overrides header-derived fields
                        metadata.update(extra_meta)  # type: ignore[arg-type]
                else:
                    message = data
        else:
            message = None

        timeout_seconds = _invoke_subscriptions(message, metadata)

        if timeout_seconds is not None:
            payload = {"timeoutSeconds": timeout_seconds}
        else:
            payload = {"ok": True}

        body = json.dumps(payload).encode("utf-8")
        start_response(
            "200 OK",
            [("Content-Type", "application/json"), ("Content-Length", str(len(body)))],
        )
        return [body]
    except Exception as exc:  # noqa: BLE001
        # Best-effort logging; real logging should be handled by the platform.
        print("vercel.workers.wsgi_app error:", repr(exc), file=sys.stderr)
        body = b'{"error":"internal"}'
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "application/json"), ("Content-Length", str(len(body)))],
        )
        return [body]


