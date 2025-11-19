"""Tests for Zaban client initialization and configuration."""

import pytest

from zaban import AsyncZaban, Zaban


def test_client_initialization_with_api_key():
    """Test client initialization with API key."""
    client = Zaban(api_key="sk-test-key")
    assert client is not None
    assert client._client.api_key == "sk-test-key"


def test_client_initialization_invalid_api_key():
    """Test client initialization with invalid API key."""
    with pytest.raises(ValueError, match="API key must start with 'sk-'"):
        Zaban(api_key="invalid-key")


def test_client_initialization_no_api_key():
    """Test client initialization without API key."""
    with pytest.raises(ValueError, match="API key is required"):
        Zaban(api_key=None)


def test_client_custom_base_url():
    """Test client with custom base URL."""
    client = Zaban(api_key="sk-test-key", base_url="https://api.example.com/v1")
    assert client._client.base_url == "https://api.example.com/v1"


def test_client_custom_timeout():
    """Test client with custom timeout."""
    client = Zaban(api_key="sk-test-key", timeout=60.0)
    assert client._client.timeout == 60.0


def test_client_context_manager():
    """Test client as context manager."""
    with Zaban(api_key="sk-test-key") as client:
        assert client is not None
    # Client should be closed after context


def test_client_repr():
    """Test client string representation."""
    client = Zaban(api_key="sk-test-key")
    repr_str = repr(client)
    assert "Zaban" in repr_str
    assert "base_url" in repr_str


def test_client_has_resources():
    """Test client has all resources."""
    client = Zaban(api_key="sk-test-key")
    assert hasattr(client, "translation")
    assert hasattr(client, "audio")
    assert hasattr(client, "transliteration")


def test_async_client_initialization():
    """Test async client initialization."""
    client = AsyncZaban(api_key="sk-test-key")
    assert client is not None
    assert client._client.api_key == "sk-test-key"


@pytest.mark.asyncio
async def test_async_client_context_manager():
    """Test async client as context manager."""
    async with AsyncZaban(api_key="sk-test-key") as client:
        assert client is not None
    # Client should be closed after context


def test_async_client_has_resources():
    """Test async client has all resources."""
    client = AsyncZaban(api_key="sk-test-key")
    assert hasattr(client, "translation")
    assert hasattr(client, "audio")
    assert hasattr(client, "transliteration")
