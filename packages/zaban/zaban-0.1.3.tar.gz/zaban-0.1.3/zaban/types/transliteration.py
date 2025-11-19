"""Transliteration type definitions."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Script(str, Enum):
    """Supported script types."""

    LATN = "latn"  # Latin
    DEVA = "deva"  # Devanagari
    BENG = "beng"  # Bengali
    TELU = "telu"  # Telugu
    TAML = "taml"  # Tamil
    GUJR = "gujr"  # Gujarati
    KNDA = "knda"  # Kannada
    MLYM = "mlym"  # Malayalam
    GURU = "guru"  # Gurmukhi
    ORYA = "orya"  # Oriya
    ARAB = "arab"  # Arabic
    MTEI = "mtei"  # Meitei
    OLCK = "olck"  # Ol Chiki


class TransliterationRequest(BaseModel):
    """Request model for transliteration."""

    text: str = Field(..., description="Text to transliterate")
    source_script: str = Field(..., description="Source script (e.g., 'latn')")
    target_script: str = Field(..., description="Target script (e.g., 'deva')")
    lang: str = Field(..., description="Language code (e.g., 'hi' for Hindi)")
    topk: Optional[int] = Field(1, description="Number of top results to return")


class TransliterationResponse(BaseModel):
    """Response model for transliteration."""

    results: List[str] = Field(..., description="List of transliterated results")
    source_script: str = Field(..., description="Source script")
    target_script: str = Field(..., description="Target script")
    language: str = Field(..., description="Language")

    def __str__(self) -> str:
        """Return the top result when converting to string."""
        return self.results[0] if self.results else ""

    @property
    def top(self) -> str:
        """Get the top transliteration result."""
        return self.results[0] if self.results else ""
