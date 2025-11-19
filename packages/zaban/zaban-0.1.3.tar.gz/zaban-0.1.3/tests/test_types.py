"""Tests for type definitions and models."""

import pytest
from pydantic import ValidationError

from zaban.types import (
    LanguageCode,
    STTRequest,
    STTResponse,
    TranslationRequest,
    TranslationResponse,
    TransliterationRequest,
    TransliterationResponse,
    TTSRequest,
    TTSResponse,
)


def test_translation_request_validation():
    """Test TranslationRequest validation."""
    request = TranslationRequest(text="Hello", source_lang="eng_Latn", target_lang="hin_Deva")

    assert request.text == "Hello"
    assert request.source_lang == "eng_Latn"
    assert request.target_lang == "hin_Deva"


def test_translation_request_missing_required():
    """Test TranslationRequest with missing required fields."""
    with pytest.raises(ValidationError):
        TranslationRequest(text="Hello")  # Missing target_lang


def test_translation_response():
    """Test TranslationResponse."""
    response = TranslationResponse(
        translated_text="नमस्ते", source_lang="eng_Latn", target_lang="hin_Deva", model="test"
    )

    assert response.translated_text == "नमस्ते"
    assert str(response) == "नमस्ते"


def test_tts_request():
    """Test TTSRequest."""
    request = TTSRequest(text="Hello", lang="hi", speaker="female")

    assert request.text == "Hello"
    assert request.lang == "hi"
    assert request.speaker == "female"


def test_tts_response():
    """Test TTSResponse."""
    import base64

    audio_data = b"fake audio data"
    encoded = base64.b64encode(audio_data).decode()

    response = TTSResponse(audio_base64=encoded, format="wav")

    assert response.content == audio_data
    assert response.format == "wav"


def test_stt_request():
    """Test STTRequest."""
    request = STTRequest(audio="path/to/audio.wav", lang="hi")

    assert request.audio == "path/to/audio.wav"
    assert request.lang == "hi"


def test_stt_response():
    """Test STTResponse."""
    response = STTResponse(text="नमस्ते", language="hi")

    assert response.text == "नमस्ते"
    assert str(response) == "नमस्ते"


def test_transliteration_request():
    """Test TransliterationRequest."""
    request = TransliterationRequest(
        text="namaste", source_script="latn", target_script="deva", lang="hi"
    )

    assert request.text == "namaste"
    assert request.source_script == "latn"
    assert request.target_script == "deva"


def test_transliteration_response():
    """Test TransliterationResponse."""
    response = TransliterationResponse(
        results=["नमस्ते", "नमस्ते"], source_script="latn", target_script="deva", language="hi"
    )

    assert len(response.results) == 2
    assert response.top == "नमस्ते"
    assert str(response) == "नमस्ते"


def test_language_code_enum():
    """Test LanguageCode enum."""
    assert LanguageCode.ENG_LATN == "eng_Latn"
    assert LanguageCode.HIN_DEVA == "hin_Deva"
    assert LanguageCode.TAM_TAML == "tam_Taml"

    # Test enum membership
    assert "eng_Latn" in [e.value for e in LanguageCode]
