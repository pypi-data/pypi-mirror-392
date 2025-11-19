"""Text-to-Speech type definitions."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"


class Speaker(str, Enum):
    """Supported speaker types."""

    MALE = "male"
    FEMALE = "female"


class TTSRequest(BaseModel):
    """Request model for Text-to-Speech."""

    text: str = Field(..., description="Text to convert to speech")
    lang: str = Field(..., description="Language code (e.g., 'hi' for Hindi)")
    speaker: Optional[str] = Field("female", description="Speaker voice (male/female)")
    sample_rate: Optional[int] = Field(22050, description="Audio sample rate")
    format: Optional[str] = Field("wav", description="Audio format (wav/mp3/flac)")


class TTSResponse(BaseModel):
    """Response model for Text-to-Speech."""

    audio_url: Optional[str] = Field(None, description="URL to download audio file")
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio data")
    format: str = Field(..., description="Audio format")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")

    @property
    def content(self) -> Optional[bytes]:
        """Get audio content as bytes."""
        if self.audio_base64:
            import base64

            return base64.b64decode(self.audio_base64)
        return None

    def save(self, filepath: str) -> None:
        """Save audio to file.

        Args:
            filepath: Path to save the audio file
        """
        content = self.content
        if content:
            with open(filepath, "wb") as f:
                f.write(content)
        else:
            raise ValueError("No audio content available")
