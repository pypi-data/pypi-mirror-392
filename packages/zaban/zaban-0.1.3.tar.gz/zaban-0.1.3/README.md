# Zaban Python Client

[![PyPI version](https://badge.fury.io/py/zaban.svg)](https://badge.fury.io/py/zaban)
[![Python Support](https://img.shields.io/pypi/pyversions/zaban.svg)](https://pypi.org/project/zaban/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python client for **Zaban API** - providing access to Zaban services for Indian languages including translation, text-to-speech, speech-to-text, and transliteration.

## 🌟 Features

- **Translation**: Powered by IndicTrans2, supporting 22 Indian languages
- **Text-to-Speech (TTS)**: Convert text to natural-sounding speech
- **Speech-to-Text (STT)**: Transcribe audio to text
- **Transliteration**: Convert text between different scripts
- **Async Support**: Full async/await support for concurrent operations
- **Type Safe**: Fully typed with Pydantic models
- **Simple API**: Clean, intuitive interface similar to OpenAI's client

## 📦 Installation

```bash
pip install zaban
```

## 🚀 Quick Start

```python
from zaban import Zaban

# Initialize client with API key
client = Zaban(api_key="sk-your-api-key")

# Or use environment variable ZABAN_API_KEY
client = Zaban()

# Translate text
result = client.translation.create(
    text="Hello, how are you?",
    source_lang="eng_Latn",
    target_lang="hin_Deva"
)
print(result.translated_text)  # "आप कैसे हैं?"
```

## 📖 Usage Examples

### Translation

```python
# English to Hindi
result = client.translation.create(
    text="Hello, how are you?",
    source_lang="eng_Latn",
    target_lang="hin_Deva"
)
print(result.translated_text)  # "आप कैसे हैं?"

# Auto-detect source language
result = client.translation.create(
    text="Hello",
    target_lang="hin_Deva",
    auto_detect=True
)

# Using convenience method
result = client.translation.translate(
    "Hello",
    to="hin_Deva",
    from_="eng_Latn"
)
```

### Text-to-Speech (TTS)

```python
# Generate speech from text
audio = client.audio.speech.create(
    text="नमस्ते दुनिया",
    lang="hi",
    speaker="female",
    format="wav"
)

# Save to file
audio.save("output.wav")

# Or get bytes directly
audio_bytes = audio.content
```

### Speech-to-Text (STT)

```python
# Transcribe from file path
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

# From audio URL
transcription = client.audio.transcriptions.create(
    audio_url="https://example.com/audio.wav",
    lang="hi"
)
```

### Transliteration

```python
# Transliterate from Latin to Devanagari
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

## ⚡ Async Support

```python
import asyncio
from zaban import AsyncZaban

async def main():
    # Initialize async client
    async with AsyncZaban(api_key="sk-your-api-key") as client:
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

asyncio.run(main())
```

## 🌐 Supported Languages

The Zaban API supports 22 Indian languages plus English using BCP-47 format with script:

| Language | Code | Script |
|----------|------|--------|
| English | `eng_Latn` | Latin |
| Hindi | `hin_Deva` | Devanagari |
| Bengali | `ben_Beng` | Bengali |
| Tamil | `tam_Taml` | Tamil |
| Telugu | `tel_Telu` | Telugu |
| Gujarati | `guj_Gujr` | Gujarati |
| Kannada | `kan_Knda` | Kannada |
| Malayalam | `mal_Mlym` | Malayalam |
| Marathi | `mar_Deva` | Devanagari |
| Punjabi | `pan_Guru` | Gurmukhi |
| Oriya | `ory_Orya` | Oriya |
| Assamese | `asm_Beng` | Bengali |
| Urdu | `urd_Arab` | Arabic |

[See full list in documentation]

## 🔧 Configuration

### Environment Variables

```bash
# Set API key
export ZABAN_API_KEY="sk-your-api-key"

# Alternative
export ZABAN_KEY="sk-your-api-key"
```

### Client Options

```python
client = Zaban(
    api_key="sk-your-api-key",       # API key
    base_url="http://localhost:8000/api/v1",  # API base URL
    timeout=30.0,                     # Request timeout in seconds
    max_retries=2,                    # Max retries for failed requests
)
```

## 🛡️ Error Handling

```python
from zaban import (
    Zaban,
    ZabanError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
    TimeoutError,
    ConnectionError,
)

try:
    result = client.translation.create(
        text="Hello",
        target_lang="hin_Deva"
    )
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except ValidationError as e:
    print(f"Invalid request: {e}")
except TimeoutError as e:
    print(f"Request timed out: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ZabanError as e:
    print(f"API error: {e}")
```

## 🔑 Getting an API Key

1. Sign up at [Zaban Dashboard]
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key (starts with `sk-`)
5. Use it in your client initialization

## 📚 Examples

Check out the [`examples/`](examples/) directory for more usage examples:

- [`basic_usage.py`](examples/basic_usage.py) - Basic usage examples
- [`async_usage.py`](examples/async_usage.py) - Async/await examples
- [`batch_translation.py`](examples/batch_translation.py) - Batch processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/prajjwalkumarpanzade/zaban-client)
- [Zaban API Documentation](https://zaban.ai/docs)
- [AI4Bharat](https://ai4bharat.org)
- [IndicTrans2](https://github.com/AI4Bharat/IndicTrans2)

## 💬 Support

- GitHub Issues: [Report bugs or request features](https://github.com/prajjwalkumarpanzade/zaban-client/issues)
- Email: support@zaban.ai

## 🙏 Acknowledgments

Built with ❤️ using AI4Bharat's amazing open-source models:
- [IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) for translation
- AI4Bharat TTS/STT services for speech processing

---

**Note**: This is an unofficial client. For official API documentation.

