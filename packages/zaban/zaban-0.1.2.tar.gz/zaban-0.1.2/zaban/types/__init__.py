"""Type definitions for Zaban API."""

from .common import LanguageCode
from .translation import TranslationRequest, TranslationResponse
from .tts import TTSRequest, TTSResponse, AudioFormat, Speaker
from .stt import STTRequest, STTResponse
from .transliteration import TransliterationRequest, TransliterationResponse, Script

__all__ = [
    "LanguageCode",
    "TranslationRequest",
    "TranslationResponse",
    "TTSRequest",
    "TTSResponse",
    "AudioFormat",
    "Speaker",
    "STTRequest",
    "STTResponse",
    "TransliterationRequest",
    "TransliterationResponse",
    "Script",
]

