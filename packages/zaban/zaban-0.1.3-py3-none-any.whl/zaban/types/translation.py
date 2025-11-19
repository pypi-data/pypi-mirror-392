"""Translation type definitions."""

from typing import Optional

from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request model for translation."""

    text: str = Field(..., description="Text to translate")
    source_lang: Optional[str] = Field(
        None, description="Source language code (e.g., 'eng_Latn'). Leave empty for auto-detection."
    )
    target_lang: str = Field(..., description="Target language code (e.g., 'hin_Deva')")
    domain: Optional[str] = Field(None, description="Translation domain (optional)")
    auto_detect: Optional[bool] = Field(
        False, description="Enable automatic language detection for source language"
    )


class TranslationResponse(BaseModel):
    """Response model for translation."""

    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    model: str = Field(..., description="Translation model used")
    auto_detected: Optional[bool] = Field(
        False, description="Whether source language was auto-detected"
    )

    def __str__(self) -> str:
        """Return the translated text when converting to string."""
        return self.translated_text
