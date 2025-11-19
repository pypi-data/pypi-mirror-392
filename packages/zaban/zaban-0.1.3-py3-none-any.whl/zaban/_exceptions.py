"""Exception classes for the Zaban API client."""

from typing import Any, Optional


class ZabanError(Exception):
    """Base exception for all Zaban errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(ZabanError):
    """Raised when API key authentication fails."""

    def __init__(self, message: str = "Invalid or missing API key", **kwargs):
        super().__init__(message, **kwargs)


class RateLimitError(ZabanError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(ZabanError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Request validation failed", **kwargs):
        super().__init__(message, **kwargs)


class APIError(ZabanError):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class TimeoutError(ZabanError):
    """Raised when request times out."""

    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(message, **kwargs)


class ConnectionError(ZabanError):
    """Raised when connection to API fails."""

    def __init__(self, message: str = "Failed to connect to API", **kwargs):
        super().__init__(message, **kwargs)


class UnsupportedLanguageError(ZabanError):
    """Raised when an unsupported language code is used."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)
