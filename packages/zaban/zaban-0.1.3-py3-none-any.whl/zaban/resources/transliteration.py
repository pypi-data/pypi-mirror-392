"""Transliteration resource for Zaban API."""

from typing import TYPE_CHECKING

from ..types.transliteration import TransliterationRequest, TransliterationResponse

if TYPE_CHECKING:
    from .._client import AsyncBaseClient, BaseClient


class Transliteration:
    """Transliteration resource for sync client."""

    def __init__(self, client: "BaseClient"):
        """Initialize transliteration resource.

        Args:
            client: Base HTTP client
        """
        self._client = client

    def create(
        self,
        *,
        text: str,
        source_script: str,
        target_script: str,
        lang: str,
        topk: int = 1,
    ) -> TransliterationResponse:
        """Transliterate text from one script to another.

        Args:
            text: Text to transliterate
            source_script: Source script (e.g., 'latn' for Latin)
            target_script: Target script (e.g., 'deva' for Devanagari)
            lang: Language code (e.g., 'hi' for Hindi)
            topk: Number of top results to return

        Returns:
            TransliterationResponse with transliterated results

        Example:
            ```python
            result = client.transliteration.create(
                text="namaste",
                source_script="latn",
                target_script="deva",
                lang="hi",
                topk=3
            )
            print(result.top)  # "नमस्ते"
            print(result.results)  # ["नमस्ते", "नमस्ते", "नमस्ते"]
            ```
        """
        request = TransliterationRequest(
            text=text,
            source_script=source_script,
            target_script=target_script,
            lang=lang,
            topk=topk,
        )

        response_data = self._client.request(
            method="POST",
            path="/transliterate",
            json=request.model_dump(),
        )

        return TransliterationResponse(**response_data)


class AsyncTransliteration:
    """Transliteration resource for async client."""

    def __init__(self, client: "AsyncBaseClient"):
        """Initialize async transliteration resource.

        Args:
            client: Async base HTTP client
        """
        self._client = client

    async def create(
        self,
        *,
        text: str,
        source_script: str,
        target_script: str,
        lang: str,
        topk: int = 1,
    ) -> TransliterationResponse:
        """Transliterate text from one script to another (async).

        Args:
            text: Text to transliterate
            source_script: Source script (e.g., 'latn' for Latin)
            target_script: Target script (e.g., 'deva' for Devanagari)
            lang: Language code (e.g., 'hi' for Hindi)
            topk: Number of top results to return

        Returns:
            TransliterationResponse with transliterated results
        """
        request = TransliterationRequest(
            text=text,
            source_script=source_script,
            target_script=target_script,
            lang=lang,
            topk=topk,
        )

        response_data = await self._client.request(
            method="POST",
            path="/transliterate",
            json=request.model_dump(),
        )

        return TransliterationResponse(**response_data)
