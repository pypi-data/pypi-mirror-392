"""Tests for translation functionality."""

from unittest.mock import patch

import pytest

from zaban import AsyncZaban, Zaban
from zaban.types import TranslationResponse


@pytest.fixture
def mock_translation_response():
    """Mock translation API response."""
    return {
        "translated_text": "आप कैसे हैं?",
        "source_lang": "eng_Latn",
        "target_lang": "hin_Deva",
        "model": "indictrans2-local",
        "auto_detected": False,
    }


def test_translation_create(mock_translation_response):
    """Test translation.create() method."""
    client = Zaban(api_key="sk-test-key")

    with patch.object(client._client, "request", return_value=mock_translation_response):
        result = client.translation.create(
            text="How are you?", source_lang="eng_Latn", target_lang="hin_Deva"
        )

        assert isinstance(result, TranslationResponse)
        assert result.translated_text == "आप कैसे हैं?"
        assert result.source_lang == "eng_Latn"
        assert result.target_lang == "hin_Deva"
        assert result.model == "indictrans2-local"


def test_translation_with_auto_detect(mock_translation_response):
    """Test translation with auto-detection."""
    client = Zaban(api_key="sk-test-key")

    mock_translation_response["auto_detected"] = True

    with patch.object(client._client, "request", return_value=mock_translation_response):
        result = client.translation.create(text="Hello", target_lang="hin_Deva", auto_detect=True)

        assert result.auto_detected is True


def test_translation_convenience_method():
    """Test translation.translate() convenience method."""
    client = Zaban(api_key="sk-test-key")

    mock_response = {
        "translated_text": "धन्यवाद",
        "source_lang": "eng_Latn",
        "target_lang": "hin_Deva",
        "model": "indictrans2-local",
        "auto_detected": False,
    }

    with patch.object(client._client, "request", return_value=mock_response):
        result = client.translation.translate("Thank you", to="hin_Deva", from_="eng_Latn")

        assert result.translated_text == "धन्यवाद"


def test_translation_response_str():
    """Test TranslationResponse __str__ method."""
    response = TranslationResponse(
        translated_text="नमस्ते",
        source_lang="eng_Latn",
        target_lang="hin_Deva",
        model="test",
    )

    assert str(response) == "नमस्ते"


@pytest.mark.asyncio
async def test_async_translation_create(mock_translation_response):
    """Test async translation.create() method."""
    client = AsyncZaban(api_key="sk-test-key")

    with patch.object(
        client._client, "request", return_value=mock_translation_response
    ) as mock_request:
        # Make the mock return a coroutine
        async def async_request(*args, **kwargs):
            return mock_translation_response

        mock_request.side_effect = async_request

        result = await client.translation.create(
            text="How are you?", source_lang="eng_Latn", target_lang="hin_Deva"
        )

        assert isinstance(result, TranslationResponse)
        assert result.translated_text == "आप कैसे हैं?"


@pytest.mark.asyncio
async def test_async_translation_batch():
    """Test async batch translations."""
    import asyncio

    client = AsyncZaban(api_key="sk-test-key")

    mock_responses = [
        {
            "translated_text": "नमस्ते",
            "source_lang": "eng_Latn",
            "target_lang": "hin_Deva",
            "model": "test",
            "auto_detected": False,
        },
        {
            "translated_text": "धन्यवाद",
            "source_lang": "eng_Latn",
            "target_lang": "hin_Deva",
            "model": "test",
            "auto_detected": False,
        },
    ]

    async def mock_request(*args, **kwargs):
        # Return different responses based on call
        return mock_responses.pop(0) if mock_responses else {}

    with patch.object(client._client, "request", side_effect=mock_request):
        texts = ["Hello", "Thank you"]
        tasks = [
            client.translation.create(text=t, target_lang="hin_Deva", auto_detect=True)
            for t in texts
        ]
        results = await asyncio.gather(*tasks)

        assert len(results) == 2
        assert results[0].translated_text == "नमस्ते"
        assert results[1].translated_text == "धन्यवाद"
