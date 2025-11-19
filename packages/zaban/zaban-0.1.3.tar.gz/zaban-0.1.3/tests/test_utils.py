"""Tests for utility functions."""

import pytest

from zaban._utils import (
    SUPPORTED_LANGUAGES,
    get_api_key_from_env,
    validate_api_key,
    validate_language_code,
)


def test_get_api_key_from_env(monkeypatch):
    """Test getting API key from environment."""
    monkeypatch.setenv("ZABAN_API_KEY", "sk-test-key")
    assert get_api_key_from_env() == "sk-test-key"


def test_get_api_key_from_env_alternative(monkeypatch):
    """Test getting API key from alternative env variable."""
    monkeypatch.delenv("ZABAN_API_KEY", raising=False)
    monkeypatch.setenv("ZABAN_KEY", "sk-alt-key")
    assert get_api_key_from_env() == "sk-alt-key"


def test_get_api_key_from_env_none(monkeypatch):
    """Test getting API key when not set."""
    monkeypatch.delenv("ZABAN_API_KEY", raising=False)
    monkeypatch.delenv("ZABAN_KEY", raising=False)
    assert get_api_key_from_env() is None


def test_validate_api_key_valid():
    """Test validating valid API key."""
    assert validate_api_key("sk-test-key") == "sk-test-key"


def test_validate_api_key_invalid_format():
    """Test validating invalid API key format."""
    with pytest.raises(ValueError, match="API key must start with 'sk-'"):
        validate_api_key("invalid-key")


def test_validate_api_key_none():
    """Test validating None API key."""
    with pytest.raises(ValueError, match="API key is required"):
        validate_api_key(None)


def test_validate_api_key_empty():
    """Test validating empty API key."""
    with pytest.raises(ValueError, match="API key is required"):
        validate_api_key("")


def test_validate_language_code_valid():
    """Test validating valid language codes."""
    assert validate_language_code("eng_Latn") == "eng_Latn"
    assert validate_language_code("hin_Deva") == "hin_Deva"
    assert validate_language_code("tam_Taml") == "tam_Taml"


def test_validate_language_code_invalid():
    """Test validating invalid language code."""
    with pytest.raises(ValueError, match="Unsupported language code"):
        validate_language_code("invalid_Lang")


def test_supported_languages():
    """Test SUPPORTED_LANGUAGES dictionary."""
    assert "eng_Latn" in SUPPORTED_LANGUAGES
    assert "hin_Deva" in SUPPORTED_LANGUAGES
    assert len(SUPPORTED_LANGUAGES) == 23  # 22 Indian languages + English

    # Check some specific languages
    assert SUPPORTED_LANGUAGES["eng_Latn"] == "English (Latin)"
    assert SUPPORTED_LANGUAGES["hin_Deva"] == "Hindi (Devanagari)"
    assert SUPPORTED_LANGUAGES["tam_Taml"] == "Tamil (Tamil)"
