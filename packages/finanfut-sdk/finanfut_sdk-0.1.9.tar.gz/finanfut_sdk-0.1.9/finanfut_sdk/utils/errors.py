"""Error hierarchy for the FinanFut SDK."""

from __future__ import annotations

from typing import Any, Dict, Optional


from typing import Any, Dict, Optional


class FinanFutApiError(Exception):
    """Base exception for all API related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(FinanFutApiError):
    """Raised when authentication fails."""


class RateLimitError(FinanFutApiError):
    """Raised when API rate limits are exceeded."""


class BillingError(FinanFutApiError):
    """Raised for billing-related issues."""


class ValidationError(FinanFutApiError):
    """Raised for invalid payloads or parameters."""


class ServerError(FinanFutApiError):
    """Raised when the FinanFut backend reports an error."""


class RequestTimeoutError(FinanFutApiError):
    """Raised when polling for an asynchronous request exceeds the timeout."""


def map_api_error(status_code: int, payload: Optional[Dict[str, Any]] = None) -> FinanFutApiError:
    """Map backend error payloads to the SDK's typed exceptions."""

    error_data: Dict[str, Any] = {}
    if isinstance(payload, dict):
        if isinstance(payload.get("error"), dict):
            error_data = payload["error"].copy()
        else:
            error_data = payload.copy()

    message = error_data.get("message") or error_data.get("detail")
    if not message:
        message = f"Request failed with status code {status_code}"

    error_code = (error_data.get("code") or "").lower()

    if status_code in (401, 403):
        return AuthenticationError(message, status_code)
    if status_code == 402 or error_code == "billing_error":
        return BillingError(message, status_code)
    if status_code == 429 or error_code == "rate_limit":
        return RateLimitError(message, status_code)
    if status_code in (400, 404, 409) or error_code == "validation_error":
        return ValidationError(message, status_code)
    if status_code >= 500:
        return ServerError(message, status_code)
    return FinanFutApiError(message, status_code)
