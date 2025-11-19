"""Main Zaban client classes."""

from typing import Optional

from ._client import AsyncBaseClient, BaseClient
from ._utils import get_api_key_from_env, validate_api_key
from .resources import (
    AsyncAudio,
    AsyncTranslation,
    AsyncTransliteration,
    Audio,
    Translation,
    Transliteration,
)


class Zaban:
    """Synchronous Zaban API client.

    This client provides access to all Zaban API services:
    - Translation (IndicTrans2)
    - Text-to-Speech (TTS)
    - Speech-to-Text (STT)
    - Transliteration

    Example:
        ```python
        from zaban import Zaban

        # Initialize with API key
        client = Zaban(api_key="sk-your-api-key")

        # Or use environment variable ZABAN_API_KEY
        client = Zaban()

        # Translate text
        result = client.translation.create(
            text="Hello, how are you?",
            source_lang="eng_Latn",
            target_lang="hin_Deva"
        )
        print(result.translated_text)

        # Text-to-Speech
        audio = client.audio.speech.create(
            text="नमस्ते",
            lang="hi",
            speaker="female"
        )
        audio.save("output.wav")

        # Speech-to-Text
        transcription = client.audio.transcriptions.create(
            audio="audio.wav",
            lang="hi"
        )
        print(transcription.text)

        # Transliteration
        result = client.transliteration.create(
            text="namaste",
            source_script="latn",
            target_script="deva",
            lang="hi"
        )
        print(result.top)
        ```
    """

    translation: Translation
    audio: Audio
    transliteration: Transliteration

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the Zaban client.

        Args:
            api_key: Zaban API key (starts with 'sk-'). If not provided,
                    will attempt to read from ZABAN_API_KEY environment variable.
            base_url: Base URL for the Zaban API. Defaults to localhost for development.
            timeout: Request timeout in seconds. Defaults to 30.0.
            max_retries: Maximum number of retries for failed requests. Defaults to 2.

        Raises:
            ValueError: If API key is not provided and not found in environment variables.
        """
        # Get API key from parameter or environment
        if api_key is None:
            api_key = get_api_key_from_env()

        # Validate API key
        api_key = validate_api_key(api_key)

        # Create base HTTP client
        self._client = BaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize resources
        self.translation = Translation(self._client)
        self.audio = Audio(self._client)
        self.transliteration = Transliteration(self._client)

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"Zaban(base_url={self._client.base_url!r})"


class AsyncZaban:
    """Asynchronous Zaban API client.

    This client provides async access to all Zaban API services.
    Use this client for async/await patterns and concurrent requests.

    Example:
        ```python
        import asyncio
        from zaban import AsyncZaban

        async def main():
            # Initialize client
            client = AsyncZaban(api_key="sk-your-api-key")

            # Single translation
            result = await client.translation.create(
                text="Hello",
                target_lang="hin_Deva",
                auto_detect=True
            )
            print(result.translated_text)

            # Batch translations (concurrent)
            texts = ["Hello", "Goodbye", "Thank you"]
            tasks = [
                client.translation.create(text=t, target_lang="hin_Deva", auto_detect=True)
                for t in texts
            ]
            results = await asyncio.gather(*tasks)

            for result in results:
                print(result.translated_text)

            # Close client
            await client.close()

        asyncio.run(main())

        # Or use as async context manager
        async def main():
            async with AsyncZaban(api_key="sk-your-api-key") as client:
                result = await client.translation.create(
                    text="Hello",
                    target_lang="hin_Deva"
                )
                print(result.translated_text)
        ```
    """

    translation: AsyncTranslation
    audio: AsyncAudio
    transliteration: AsyncTransliteration

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the async Zaban client.

        Args:
            api_key: Zaban API key (starts with 'sk-'). If not provided,
                    will attempt to read from ZABAN_API_KEY environment variable.
            base_url: Base URL for the Zaban API. Defaults to localhost for development.
            timeout: Request timeout in seconds. Defaults to 30.0.
            max_retries: Maximum number of retries for failed requests. Defaults to 2.

        Raises:
            ValueError: If API key is not provided and not found in environment variables.
        """
        # Get API key from parameter or environment
        if api_key is None:
            api_key = get_api_key_from_env()

        # Validate API key
        api_key = validate_api_key(api_key)

        # Create async base HTTP client
        self._client = AsyncBaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize async resources
        self.translation = AsyncTranslation(self._client)
        self.audio = AsyncAudio(self._client)
        self.transliteration = AsyncTransliteration(self._client)

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"AsyncZaban(base_url={self._client.base_url!r})"
