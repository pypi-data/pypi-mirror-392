from __future__ import annotations

from typing import Any, Optional


class LoceZapError(Exception):
    """Base error para a SDK."""

    def __init__(self, message: str, *, response: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.response = response

    def __str__(self) -> str:
        return self.message


class AuthenticationError(LoceZapError):
    """Quando a API rejeita a api_key/token."""


class AuthorizationError(LoceZapError):
    """Raised when the user has no permission to access a resource."""


class RateLimitError(LoceZapError):
    """Raised when the API rate limit or daily quota is exceeded."""


class ValidationError(LoceZapError):
    """Raised when the API returns a 400 due to invalid payload."""


class NotFoundError(LoceZapError):
    """Recurso inexistente."""


class ServerError(LoceZapError):
    """Falhas 5xx na API."""


class TransportError(LoceZapError):
    """Falhas de rede, timeouts ou parsing."""


class APIError(LoceZapError):
    """Generic 4xx error returned by the API."""


class WebhookSignatureError(LoceZapError):
    """Webhook signature does not match the expected HMAC."""
