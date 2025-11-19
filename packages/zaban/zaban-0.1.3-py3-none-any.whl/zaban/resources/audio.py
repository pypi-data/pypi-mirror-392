"""Audio resources (TTS and STT) for Zaban API."""

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Optional, Union

from ..types.stt import STTResponse
from ..types.tts import TTSRequest, TTSResponse

if TYPE_CHECKING:
    from .._client import AsyncBaseClient, BaseClient


class Speech:
    """Text-to-Speech resource for sync client."""

    def __init__(self, client: "BaseClient"):
        """Initialize TTS resource.

        Args:
            client: Base HTTP client
        """
        self._client = client

    def create(
        self,
        *,
        text: str,
        lang: str,
        speaker: str = "female",
        sample_rate: int = 22050,
        format: str = "wav",
    ) -> TTSResponse:
        """Generate speech from text.

        Args:
            text: Text to convert to speech
            lang: Language code (e.g., 'hi' for Hindi)
            speaker: Speaker voice ('male' or 'female')
            sample_rate: Audio sample rate
            format: Audio format ('wav', 'mp3', or 'flac')

        Returns:
            TTSResponse with audio data

        Example:
            ```python
            audio = client.audio.speech.create(
                text="नमस्ते दुनिया",
                lang="hi",
                speaker="female"
            )
            audio.save("output.wav")
            ```
        """
        request = TTSRequest(
            text=text,
            lang=lang,
            speaker=speaker,
            sample_rate=sample_rate,
            format=format,
        )

        response_data = self._client.request(
            method="POST",
            path="/tts",
            json=request.model_dump(),
        )

        return TTSResponse(**response_data)


class Transcriptions:
    """Speech-to-Text resource for sync client."""

    def __init__(self, client: "BaseClient"):
        """Initialize STT resource.

        Args:
            client: Base HTTP client
        """
        self._client = client

    def create(
        self,
        *,
        audio: Union[str, Path, BinaryIO, bytes],
        lang: str,
        audio_url: Optional[str] = None,
    ) -> STTResponse:
        """Transcribe audio to text.

        Args:
            audio: Audio file (path, file object, or bytes)
            lang: Language code (e.g., 'hi' for Hindi)
            audio_url: URL to audio file (alternative to audio parameter)

        Returns:
            STTResponse with transcribed text

        Example:
            ```python
            # From file path
            transcription = client.audio.transcriptions.create(
                audio="audio.wav",
                lang="hi"
            )
            print(transcription.text)

            # From file object
            with open("audio.wav", "rb") as f:
                transcription = client.audio.transcriptions.create(
                    audio=f,
                    lang="hi"
                )
            ```
        """
        # If audio_url is provided, use JSON request
        if audio_url:
            response_data = self._client.request(
                method="POST",
                path="/stt",
                json={"audio_url": audio_url, "lang": lang},
            )
        else:
            # Handle file upload
            if isinstance(audio, (str, Path)):
                with open(audio, "rb") as f:
                    audio_content = f.read()
            elif isinstance(audio, bytes):
                audio_content = audio
            else:
                audio_content = audio.read()

            response_data = self._client.request(
                method="POST",
                path="/stt",
                files={"audio": audio_content},
                params={"lang": lang},
            )

        return STTResponse(**response_data)


class Audio:
    """Audio resource (TTS and STT) for sync client."""

    def __init__(self, client: "BaseClient"):
        """Initialize audio resource.

        Args:
            client: Base HTTP client
        """
        self.speech = Speech(client)
        self.transcriptions = Transcriptions(client)


class AsyncSpeech:
    """Text-to-Speech resource for async client."""

    def __init__(self, client: "AsyncBaseClient"):
        """Initialize async TTS resource.

        Args:
            client: Async base HTTP client
        """
        self._client = client

    async def create(
        self,
        *,
        text: str,
        lang: str,
        speaker: str = "female",
        sample_rate: int = 22050,
        format: str = "wav",
    ) -> TTSResponse:
        """Generate speech from text (async).

        Args:
            text: Text to convert to speech
            lang: Language code (e.g., 'hi' for Hindi)
            speaker: Speaker voice ('male' or 'female')
            sample_rate: Audio sample rate
            format: Audio format ('wav', 'mp3', or 'flac')

        Returns:
            TTSResponse with audio data
        """
        request = TTSRequest(
            text=text,
            lang=lang,
            speaker=speaker,
            sample_rate=sample_rate,
            format=format,
        )

        response_data = await self._client.request(
            method="POST",
            path="/tts",
            json=request.model_dump(),
        )

        return TTSResponse(**response_data)


class AsyncTranscriptions:
    """Speech-to-Text resource for async client."""

    def __init__(self, client: "AsyncBaseClient"):
        """Initialize async STT resource.

        Args:
            client: Async base HTTP client
        """
        self._client = client

    async def create(
        self,
        *,
        audio: Union[str, Path, BinaryIO, bytes],
        lang: str,
        audio_url: Optional[str] = None,
    ) -> STTResponse:
        """Transcribe audio to text (async).

        Args:
            audio: Audio file (path, file object, or bytes)
            lang: Language code (e.g., 'hi' for Hindi)
            audio_url: URL to audio file (alternative to audio parameter)

        Returns:
            STTResponse with transcribed text
        """
        # If audio_url is provided, use JSON request
        if audio_url:
            response_data = await self._client.request(
                method="POST",
                path="/stt",
                json={"audio_url": audio_url, "lang": lang},
            )
        else:
            # Handle file upload
            if isinstance(audio, (str, Path)):
                with open(audio, "rb") as f:
                    audio_content = f.read()
            elif isinstance(audio, bytes):
                audio_content = audio
            else:
                audio_content = audio.read()

            response_data = await self._client.request(
                method="POST",
                path="/stt",
                files={"audio": audio_content},
                params={"lang": lang},
            )

        return STTResponse(**response_data)


class AsyncAudio:
    """Audio resource (TTS and STT) for async client."""

    def __init__(self, client: "AsyncBaseClient"):
        """Initialize async audio resource.

        Args:
            client: Async base HTTP client
        """
        self.speech = AsyncSpeech(client)
        self.transcriptions = AsyncTranscriptions(client)
