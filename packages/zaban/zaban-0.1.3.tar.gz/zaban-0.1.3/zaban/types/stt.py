"""Speech-to-Text type definitions."""

from typing import Optional, Union

from pydantic import BaseModel, Field


class STTRequest(BaseModel):
    """Request model for Speech-to-Text."""

    audio: Union[str, bytes] = Field(..., description="Audio file path or audio bytes")
    lang: str = Field(..., description="Language code (e.g., 'hi' for Hindi)")
    audio_url: Optional[str] = Field(None, description="URL to audio file (alternative to audio)")


class STTResponse(BaseModel):
    """Response model for Speech-to-Text."""

    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")

    def __str__(self) -> str:
        """Return the transcribed text when converting to string."""
        return self.text
