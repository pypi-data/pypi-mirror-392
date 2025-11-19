"""Translation resource for Zaban API."""

from typing import TYPE_CHECKING, Optional

from ..types.translation import TranslationRequest, TranslationResponse

if TYPE_CHECKING:
    from .._client import AsyncBaseClient, BaseClient


class Translation:
    """Translation resource for sync client."""

    def __init__(self, client: "BaseClient"):
        """Initialize translation resource.

        Args:
            client: Base HTTP client
        """
        self._client = client

    def create(
        self,
        *,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        auto_detect: bool = False,
        domain: Optional[str] = None,
    ) -> TranslationResponse:
        """Translate text from source language to target language.

        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'hin_Deva')
            source_lang: Source language code (optional, auto-detected if not provided)
            auto_detect: Enable automatic source language detection
            domain: Translation domain (optional)

        Returns:
            TranslationResponse with translated text

        Example:
            ```python
            # English to Hindi
            result = client.translation.create(
                text="Hello, how are you?",
                source_lang="eng_Latn",
                target_lang="hin_Deva"
            )
            print(result.translated_text)  # "आप कैसे हैं?"

            # With auto-detection
            result = client.translation.create(
                text="Hello",
                target_lang="hin_Deva",
                auto_detect=True
            )
            ```
        """
        request = TranslationRequest(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            domain=domain,
            auto_detect=auto_detect,
        )

        response_data = self._client.request(
            method="POST",
            path="/translate",
            json=request.model_dump(exclude_none=True),
        )

        return TranslationResponse(**response_data)

    def translate(
        self,
        text: str,
        *,
        to: str,
        from_: Optional[str] = None,
        auto_detect: bool = False,
    ) -> TranslationResponse:
        """Convenience method for translation with simpler parameter names.

        Args:
            text: Text to translate
            to: Target language code
            from_: Source language code (optional)
            auto_detect: Enable automatic source language detection

        Returns:
            TranslationResponse with translated text

        Example:
            ```python
            result = client.translation.translate(
                "Hello",
                to="hin_Deva",
                from_="eng_Latn"
            )
            ```
        """
        return self.create(
            text=text,
            target_lang=to,
            source_lang=from_,
            auto_detect=auto_detect,
        )


class AsyncTranslation:
    """Translation resource for async client."""

    def __init__(self, client: "AsyncBaseClient"):
        """Initialize async translation resource.

        Args:
            client: Async base HTTP client
        """
        self._client = client

    async def create(
        self,
        *,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        auto_detect: bool = False,
        domain: Optional[str] = None,
    ) -> TranslationResponse:
        """Translate text from source language to target language (async).

        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'hin_Deva')
            source_lang: Source language code (optional, auto-detected if not provided)
            auto_detect: Enable automatic source language detection
            domain: Translation domain (optional)

        Returns:
            TranslationResponse with translated text

        Example:
            ```python
            result = await client.translation.create(
                text="Hello",
                target_lang="hin_Deva",
                auto_detect=True
            )
            ```
        """
        request = TranslationRequest(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            domain=domain,
            auto_detect=auto_detect,
        )

        response_data = await self._client.request(
            method="POST",
            path="/translate",
            json=request.model_dump(exclude_none=True),
        )

        return TranslationResponse(**response_data)

    async def translate(
        self,
        text: str,
        *,
        to: str,
        from_: Optional[str] = None,
        auto_detect: bool = False,
    ) -> TranslationResponse:
        """Convenience method for translation with simpler parameter names (async).

        Args:
            text: Text to translate
            to: Target language code
            from_: Source language code (optional)
            auto_detect: Enable automatic source language detection

        Returns:
            TranslationResponse with translated text
        """
        return await self.create(
            text=text,
            target_lang=to,
            source_lang=from_,
            auto_detect=auto_detect,
        )
