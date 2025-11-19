"""Zaban Python Client - Official client for Zaban API.

This package provides a simple and intuitive interface to interact with
Zaban API services including translation, text-to-speech, speech-to-text,
and transliteration for Indian languages.

Example:
    ```python
    from zaban import Zaban
    
    # Initialize client
    client = Zaban(api_key="sk-your-api-key")
    
    # Translate text
    result = client.translation.create(
        text="Hello, how are you?",
        source_lang="eng_Latn",
        target_lang="hin_Deva"
    )
    print(result.translated_text)  # "आप कैसे हैं?"
    ```
"""

from .version import __version__
from .client import Zaban, AsyncZaban
from ._exceptions import (
    ZabanError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
    TimeoutError,
    ConnectionError,
    UnsupportedLanguageError,
)
from .types import (
    LanguageCode,
    TranslationRequest,
    TranslationResponse,
    TTSRequest,
    TTSResponse,
    AudioFormat,
    Speaker,
    STTRequest,
    STTResponse,
    TransliterationRequest,
    TransliterationResponse,
    Script,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "Zaban",
    "AsyncZaban",
    # Exceptions
    "ZabanError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "APIError",
    "TimeoutError",
    "ConnectionError",
    "UnsupportedLanguageError",
    # Types
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

