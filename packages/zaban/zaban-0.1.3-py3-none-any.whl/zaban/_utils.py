"""Utility functions for the Zaban client."""

import os
from typing import Optional


def get_api_key_from_env() -> Optional[str]:
    """Get API key from environment variables.

    Checks ZABAN_API_KEY first, then falls back to ZABAN_KEY.

    Returns:
        API key if found, None otherwise
    """
    return os.environ.get("ZABAN_API_KEY") or os.environ.get("ZABAN_KEY")


def validate_api_key(api_key: Optional[str]) -> str:
    """Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        Validated API key

    Raises:
        ValueError: If API key is invalid
    """
    if not api_key:
        raise ValueError(
            "API key is required. Pass it as api_key parameter or set ZABAN_API_KEY environment variable."
        )

    if not api_key.startswith("sk-"):
        raise ValueError("API key must start with 'sk-'")

    return api_key


# Supported language codes (BCP-47 format with script)
SUPPORTED_LANGUAGES = {
    "eng_Latn": "English (Latin)",
    "hin_Deva": "Hindi (Devanagari)",
    "ben_Beng": "Bengali (Bengali)",
    "tel_Telu": "Telugu (Telugu)",
    "tam_Taml": "Tamil (Tamil)",
    "guj_Gujr": "Gujarati (Gujarati)",
    "kan_Knda": "Kannada (Kannada)",
    "mal_Mlym": "Malayalam (Malayalam)",
    "mar_Deva": "Marathi (Devanagari)",
    "pan_Guru": "Punjabi (Gurmukhi)",
    "ory_Orya": "Oriya (Oriya)",
    "asm_Beng": "Assamese (Bengali)",
    "urd_Arab": "Urdu (Arabic)",
    "kas_Arab": "Kashmiri (Arabic)",
    "kas_Deva": "Kashmiri (Devanagari)",
    "gom_Deva": "Konkani (Devanagari)",
    "mni_Beng": "Manipuri (Bengali)",
    "mni_Mtei": "Manipuri (Meitei)",
    "npi_Deva": "Nepali (Devanagari)",
    "san_Deva": "Sanskrit (Devanagari)",
    "sat_Olck": "Santali (Ol Chiki)",
    "snd_Arab": "Sindhi (Arabic)",
    "snd_Deva": "Sindhi (Devanagari)",
}


def validate_language_code(code: str) -> str:
    """Validate language code against supported languages.

    Args:
        code: Language code to validate

    Returns:
        Validated language code

    Raises:
        ValueError: If language code is not supported
    """
    if code not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language code: {code}. "
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        )
    return code
