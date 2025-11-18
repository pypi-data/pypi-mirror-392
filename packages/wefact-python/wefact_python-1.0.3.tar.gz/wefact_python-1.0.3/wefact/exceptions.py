from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Type

__all__ = [
    "WeFactAPIError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "ClientError",
    "from_response",
    "raise_for_response",
    "raise_for_wefact_payload",
]


class WeFactAPIError(Exception):
    """Base class for exceptions raised by the WeFact API wrapper.

    Carries structured context to aid debugging and alignment with WeFact docs.

    Attributes:
        message: Human-readable error message.
        status: HTTP status code (if available).
        code: API-specific error code (if available).
        details: Additional error details/payload (dict, list, or raw body).
        request_id: Correlation ID from response headers if provided by the API.
        response: Original response object (requests/httpx) for debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        details: Any = None,
        request_id: Optional[str] = None,
        response: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.details = details
        self.request_id = request_id
        self.response = response

    def __str__(self) -> str:
        parts = []
        if self.status is not None:
            parts.append(str(self.status))
        if self.code:
            parts.append(self.code)
        prefix = " ".join(parts)
        base = f"{prefix}: {self.message}" if prefix else self.message
        if self.request_id:
            return f"{base} (request_id={self.request_id})"
        return base


class AuthenticationError(WeFactAPIError):
    """Exception raised for authentication/authorization errors."""
    pass


class NotFoundError(WeFactAPIError):
    """Exception raised when a requested resource is not found."""
    pass


class ValidationError(WeFactAPIError):
    """Exception raised for validation errors in API requests."""
    pass


class ServerError(WeFactAPIError):
    """Exception raised for server errors (5xx responses)."""
    pass


class ClientError(WeFactAPIError):
    """Exception raised for client errors (4xx responses)."""
    pass


def _pick_exception_class(status: Optional[int]) -> Type[WeFactAPIError]:
    """Map HTTP status to a specific exception class."""
    if status is None:
        return WeFactAPIError
    if status in (401, 403):
        return AuthenticationError
    if status == 404:
        return NotFoundError
    if status in (400, 422):
        return ValidationError
    if 400 <= status < 500:
        return ClientError
    if status >= 500:
        return ServerError
    return WeFactAPIError


def _extract_error_fields(
    body: Any,
    default_message: str = "An error occurred",
) -> Tuple[str, Optional[str], Any]:
    """Attempt to extract (message, code, details) from a JSON body or text.

    WeFact typically returns a dict with keys like 'status' ('success'/'error'),
    'errors' (list of messages), or 'message'. We'll be tolerant to variations.
    """
    message: str = default_message
    code: Optional[str] = None
    details: Any = None

    if isinstance(body, dict):
        # API-specific code key if any
        code = (
            body.get("code")
            or body.get("error_code")
            or body.get("errorCode")
        )

        # Prefer explicit message; fallback to first error message
        message = (
            body.get("message")
            or body.get("error")
            or body.get("detail")
            or (body.get("errors") and "; ".join(map(str, body.get("errors") or [])))
            or default_message
        )

        # Include structured details when present
        details = body.get("errors") or body.get("details") or body
    elif isinstance(body, str) and body.strip():
        message = body.strip()
        details = body
    else:
        details = body

    return message, code, details


def from_response(response: Any) -> WeFactAPIError:
    """Create a WeFactAPIError (or subclass) from an HTTP response.

    Works with 'requests' or 'httpx' responses (duck-typed). Does not raise.
    """
    status = getattr(response, "status_code", None)

    # Attempt to parse body as JSON; fallback to text
    parsed_body: Any = None
    body_text: Optional[str] = None

    try:
        parsed_body = response.json()  # type: ignore[attr-defined]
    except Exception:
        body_text = getattr(response, "text", None)
        parsed_body = body_text if body_text is not None else None

    reason = getattr(response, "reason", None)
    default_message = f"HTTP {status}" + (f" {reason}" if reason else "")

    message, code, details = _extract_error_fields(parsed_body, default_message)

    # Try to capture a request/correlation id header if present
    headers: Dict[str, str] = {}
    try:
        headers = dict(getattr(response, "headers", {}) or {})
    except Exception:
        headers = {}
    request_id = (
        headers.get("X-Request-Id")
        or headers.get("X-Request-ID")
        or headers.get("Request-Id")
        or headers.get("Request-ID")
    )

    exc_cls = _pick_exception_class(status)
    return exc_cls(
        message,
        status=status,
        code=code,
        details=details,
        request_id=request_id,
        response=response,
    )


def raise_for_response(response: Any) -> None:
    """Raise a mapped WeFactAPIError if the response indicates an HTTP error.

    No-op if the status is in the 2xx range.
    """
    status = getattr(response, "status_code", None)
    if status is not None and 200 <= int(status) < 300:
        return
    raise from_response(response)


def raise_for_wefact_payload(response: Any, data: Optional[Dict[str, Any]] = None) -> None:
    """Raise a ValidationError (or mapped error) when WeFact returns status='error'.

    According to WeFact docs, application-level errors are reported via a JSON body
    with key 'status' equal to 'error'. In such cases, raise with the parsed details.
    """
    try:
        payload = data if data is not None else response.json()
    except Exception:
        # If body isn't JSON, fall back to HTTP-layer handling
        raise_for_response(response)
        return

    if isinstance(payload, dict) and payload.get("status") == "error":
        status_code: Optional[int] = getattr(response, "status_code", None)
        message, code, details = _extract_error_fields(payload, "WeFact API error")
        exc_cls: Type[WeFactAPIError]
        # Treat WeFact 'error' payloads as validation/client errors unless HTTP indicates otherwise
        if status_code and status_code >= 500:
            exc_cls = ServerError
        elif status_code in (401, 403):
            exc_cls = AuthenticationError
        elif status_code == 404:
            exc_cls = NotFoundError
        else:
            # Most common case for WeFact business-rule errors
            exc_cls = ValidationError
        raise exc_cls(message, status=status_code, code=code, details=details, response=response)
