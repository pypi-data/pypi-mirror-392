"""Type definitions for Zaban API."""

from .common import LanguageCode
from .stt import STTRequest, STTResponse
from .translation import TranslationRequest, TranslationResponse
from .transliteration import Script, TransliterationRequest, TransliterationResponse
from .tts import AudioFormat, Speaker, TTSRequest, TTSResponse

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
