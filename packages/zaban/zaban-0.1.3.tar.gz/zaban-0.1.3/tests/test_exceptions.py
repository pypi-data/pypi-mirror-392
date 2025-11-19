"""Tests for exception handling."""

from zaban._exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    RateLimitError,
    TimeoutError,
    UnsupportedLanguageError,
    ValidationError,
    ZabanError,
)


def test_zaban_error():
    """Test base ZabanError."""
    error = ZabanError("Test error", status_code=400)
    assert str(error) == "Test error"
    assert error.status_code == 400


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError()
    assert "Invalid or missing API key" in str(error)

    custom_error = AuthenticationError("Custom message")
    assert str(custom_error) == "Custom message"


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError()
    assert "Rate limit exceeded" in str(error)


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Invalid input")
    assert str(error) == "Invalid input"


def test_api_error():
    """Test APIError."""
    error = APIError("Server error", status_code=500)
    assert str(error) == "Server error"
    assert error.status_code == 500


def test_timeout_error():
    """Test TimeoutError."""
    error = TimeoutError()
    assert "Request timed out" in str(error)


def test_connection_error():
    """Test ConnectionError."""
    error = ConnectionError()
    assert "Failed to connect" in str(error)


def test_unsupported_language_error():
    """Test UnsupportedLanguageError."""
    error = UnsupportedLanguageError("Language xyz is not supported")
    assert "xyz" in str(error)


def test_error_inheritance():
    """Test exception inheritance."""
    assert issubclass(AuthenticationError, ZabanError)
    assert issubclass(RateLimitError, ZabanError)
    assert issubclass(ValidationError, ZabanError)
    assert issubclass(APIError, ZabanError)
