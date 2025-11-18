from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Protocol, TypedDict

import httpx

from vercel.oidc.aio import get_vercel_oidc_token

__all__ = [
    "MessageMetadata",
    "WorkerTimeoutResult",
    "subscribe",
    "wsgi_app",
    "has_subscriptions",
    "send",
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


class SendMessageResult(TypedDict):
    """Result of successfully sending a message to the queue."""

    messageId: str


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
                    extra_meta_raw = data.get("metadata") or {}
                    if isinstance(extra_meta_raw, dict):
                        # Shallow merge: body metadata overrides header-derived fields
                        extra_meta: MessageMetadata = {
                            k: v for k, v in extra_meta_raw.items() if isinstance(k, str)
                        }  # type: ignore[assignment]
                        metadata.update(extra_meta)
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
        print("vercel.workers.wsgi_app error:", repr(exc))
        body = b'{"error":"internal"}'
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "application/json"), ("Content-Length", str(len(body)))],
        )
        return [body]


def _get_queue_base_url() -> str:
    """
    Return the base URL for the Vercel Queue Service API.

    Mirrors the JS client behaviour:
      - VERCEL_QUEUE_BASE_URL environment variable
      - default to "https://vercel-queue.com"
    """
    return os.environ.get("VERCEL_QUEUE_BASE_URL", "https://vercel-queue.com").rstrip("/")


def _get_queue_base_path() -> str:
    """
    Return the base path for the queue API endpoints.

    Mirrors the JS client behaviour:
      - VERCEL_QUEUE_BASE_PATH environment variable
      - default to "/api/v2/messages"
    """
    base_path = os.environ.get("VERCEL_QUEUE_BASE_PATH", "/api/v2/messages")
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    return base_path


def _get_queue_token(explicit_token: str | None = None) -> str:
    """
    Resolve the token used to authenticate with the queue service (synchronously).

    Resolution order:
      1. An explicit ``token=...`` argument.
      2. The ``VERCEL_QUEUE_TOKEN`` environment variable.
      3. The Vercel OIDC token from ``vercel.oidc.aio.get_vercel_oidc_token``,
         resolved in a best-effort way from synchronous code.

    This helper is used by the synchronous ``send`` function.
    """
    if explicit_token:
        return explicit_token

    env_token = os.environ.get("VERCEL_QUEUE_TOKEN")
    if env_token:
        return env_token

    # Fall back to Vercel OIDC token when running inside a Vercel environment.
    # We use asyncio.run() in contexts without a running event loop. If an event
    # loop is already running, we silently skip this step and fall through to
    # the error below, encouraging callers to either pass an explicit token or
    # use the async send_async() helper instead.
    token: str | None = None
    try:
        # asyncio.run() will raise RuntimeError if called from within an
        # existing running event loop; in that case we simply treat this as
        # an unavailable OIDC token in this synchronous context.
        token = asyncio.run(get_vercel_oidc_token())
    except RuntimeError:
        token = None

    if token:
        return token

    msg = (
        "Failed to resolve queue token. Provide 'token' explicitly when calling send(), "
        "set the VERCEL_QUEUE_TOKEN environment variable, "
        "or ensure a Vercel OIDC token is available in this environment.",
    )
    raise RuntimeError(msg)


async def _get_queue_token_async(explicit_token: str | None = None) -> str:
    """
    Resolve the token used to authenticate with the queue service (asynchronously).

    Resolution order:
      1. An explicit ``token=...`` argument.
      2. The ``VERCEL_QUEUE_TOKEN`` environment variable.
      3. The Vercel OIDC token from ``vercel.oidc.aio.get_vercel_oidc_token``.
    """
    if explicit_token:
        return explicit_token

    env_token = os.environ.get("VERCEL_QUEUE_TOKEN")
    if env_token:
        return env_token

    # Fall back to Vercel OIDC token when running inside a Vercel environment.
    token = await get_vercel_oidc_token()
    if token:
        return token

    msg = (
        "Failed to resolve queue token. Provide 'token' explicitly when calling send_async(), "
        "set the VERCEL_QUEUE_TOKEN environment variable, "
        "or ensure a Vercel OIDC token is available in this environment.",
    )
    raise RuntimeError(msg)


def send(
    queue_name: str,
    payload: Any,
    *,
    idempotency_key: str | None = None,
    retention_seconds: int | None = None,
    deployment_id: str | None = None,
    token: str | None = None,
    base_url: str | None = None,
    base_path: str | None = None,
    content_type: str = "application/json",
    timeout: float | None = 10.0,
) -> SendMessageResult:
    """
    Send a message to a Vercel Queue (synchronous).

    This variant expects an explicit token or the ``VERCEL_QUEUE_TOKEN`` environment
    variable and is intended for environments where you can't easily ``await``.
    For automatic resolution via Vercel OIDC tokens, use :func:`send_async`.

    Args:
        queue_name: Name of the target queue (equivalent to ``queueName``).
        payload: Message payload. For the default JSON content type this must be JSON-serialisable.
        idempotency_key: Optional key to deduplicate submissions (``Vqs-Idempotency-Key`` header).
        retention_seconds: Optional message retention time in seconds (``Vqs-Retention-Seconds``).
        deployment_id: Optional deployment identifier (``Vqs-Deployment-Id``).
        token: Authentication token. If omitted, falls back to ``VERCEL_QUEUE_TOKEN`` env var.
        base_url: Override base URL for the queue API. Defaults to ``VERCEL_QUEUE_BASE_URL`` or
            ``https://vercel-queue.com``.
        base_path: Override base path for the messages endpoint. Defaults to
            ``VERCEL_QUEUE_BASE_PATH`` or ``/api/v2/messages``.
        content_type: MIME type of the payload. Defaults to ``application/json``.
        timeout: Optional request timeout in seconds.

    Returns:
        A dict containing the generated ``messageId``.
    """
    resolved_base_url = (base_url or _get_queue_base_url()).rstrip("/")
    resolved_base_path = base_path or _get_queue_base_path()
    auth_token = _get_queue_token(token)

    headers: dict[str, str] = {
        "Authorization": f"Bearer {auth_token}",
        "Vqs-Queue-Name": queue_name,
        "Content-Type": content_type,
    }

    deployment_id = deployment_id or os.environ.get("VERCEL_DEPLOYMENT_ID")
    if deployment_id:
        headers["Vqs-Deployment-Id"] = deployment_id

    if idempotency_key:
        headers["Vqs-Idempotency-Key"] = idempotency_key

    if retention_seconds is not None:
        headers["Vqs-Retention-Seconds"] = str(retention_seconds)

    # Basic payload handling: default to JSON, but allow callers to provide their own
    # serialisation if they change the content type.
    if content_type == "application/json":
        body: bytes = json.dumps(payload).encode("utf-8")
    elif isinstance(payload, (bytes, bytearray)):
        body = bytes(payload)
    else:
        raise TypeError(
            "Non-JSON content_type requires 'payload' to be bytes or bytearray; "
            "for structured data use the default JSON content type.",
        )

    url = f"{resolved_base_url}{resolved_base_path}"

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, content=body, headers=headers)

    # Map common error codes to Python exceptions similar to the TS client.
    if response.status_code == 400:
        raise ValueError(response.text or "Invalid parameters")
    if response.status_code == 401:
        raise PermissionError("Missing or invalid authentication token (401)")
    if response.status_code == 403:
        raise PermissionError("Queue environment does not match token environment (403)")
    if response.status_code == 409:
        raise RuntimeError("Duplicate idempotency key detected (409)")
    if response.status_code >= 500:
        msg = f"Server error: {response.status_code} {response.reason_phrase}"
        raise RuntimeError(msg)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - defensive
        raise RuntimeError(
            f"Failed to send message: {exc.response.status_code} {exc.response.reason_phrase}",
        ) from exc

    data = response.json()
    if not isinstance(data, dict) or "messageId" not in data:
        raise RuntimeError("Queue API returned an unexpected response: missing 'messageId'")

    return {"messageId": str(data["messageId"])}


async def send_async(
    queue_name: str,
    payload: Any,
    *,
    idempotency_key: str | None = None,
    retention_seconds: int | None = None,
    deployment_id: str | None = None,
    token: str | None = None,
    base_url: str | None = None,
    base_path: str | None = None,
    content_type: str = "application/json",
    timeout: float | None = 10.0,
) -> SendMessageResult:
    """
    Asynchronous variant of :func:`send` that additionally supports resolving
    tokens via the Vercel OIDC helper when running inside Vercel.

    Args:
        queue_name: Name of the target queue (equivalent to ``queueName``).
        payload: Message payload. For the default JSON content type this must be JSON-serialisable.
        idempotency_key: Optional key to deduplicate submissions (``Vqs-Idempotency-Key`` header).
        retention_seconds: Optional message retention time in seconds (``Vqs-Retention-Seconds``).
        deployment_id: Optional deployment identifier (``Vqs-Deployment-Id``).
        token: Authentication token. If omitted, falls back to ``VERCEL_QUEUE_TOKEN`` env var.
        base_url: Override base URL for the queue API. Defaults to ``VERCEL_QUEUE_BASE_URL`` or
            ``https://vercel-queue.com``.
        base_path: Override base path for the messages endpoint. Defaults to
            ``VERCEL_QUEUE_BASE_PATH`` or ``/api/v2/messages``.
        content_type: MIME type of the payload. Defaults to ``application/json``.
        timeout: Optional request timeout in seconds.

    Returns:
        A dict containing the generated ``messageId``.
    """
    resolved_base_url = (base_url or _get_queue_base_url()).rstrip("/")
    resolved_base_path = base_path or _get_queue_base_path()
    auth_token = await _get_queue_token_async(token)

    headers: dict[str, str] = {
        "Authorization": f"Bearer {auth_token}",
        "Vqs-Queue-Name": queue_name,
        "Content-Type": content_type,
    }

    deployment_id = deployment_id or os.environ.get("VERCEL_DEPLOYMENT_ID")
    if deployment_id:
        headers["Vqs-Deployment-Id"] = deployment_id

    if idempotency_key:
        headers["Vqs-Idempotency-Key"] = idempotency_key

    if retention_seconds is not None:
        headers["Vqs-Retention-Seconds"] = str(retention_seconds)

    # Basic payload handling: default to JSON, but allow callers to provide their own
    # serialisation if they change the content type.
    if content_type == "application/json":
        body: bytes = json.dumps(payload).encode("utf-8")
    elif isinstance(payload, (bytes, bytearray)):
        body = bytes(payload)
    else:
        raise TypeError(
            "Non-JSON content_type requires 'payload' to be bytes or bytearray; "
            "for structured data use the default JSON content type.",
        )

    url = f"{resolved_base_url}{resolved_base_path}"

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, content=body, headers=headers)

    # Map common error codes to Python exceptions similar to the TS client.
    if response.status_code == 400:
        raise ValueError(response.text or "Invalid parameters")
    if response.status_code == 401:
        raise PermissionError("Missing or invalid authentication token (401)")
    if response.status_code == 403:
        raise PermissionError("Queue environment does not match token environment (403)")
    if response.status_code == 409:
        raise RuntimeError("Duplicate idempotency key detected (409)")
    if response.status_code >= 500:
        msg = f"Server error: {response.status_code} {response.reason_phrase}"
        raise RuntimeError(msg)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - defensive
        raise RuntimeError(
            f"Failed to send message: {exc.response.status_code} {exc.response.reason_phrase}",
        ) from exc

    data = response.json()
    if not isinstance(data, dict) or "messageId" not in data:
        raise RuntimeError("Queue API returned an unexpected response: missing 'messageId'")

    return {"messageId": str(data["messageId"])}
