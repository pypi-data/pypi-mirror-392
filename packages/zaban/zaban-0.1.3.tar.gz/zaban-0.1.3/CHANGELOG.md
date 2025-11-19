# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-17

### Added
- Initial release of Zaban Python client
- Translation support for 22 Indian languages via IndicTrans2
- Text-to-Speech (TTS) functionality
- Speech-to-Text (STT) functionality
- Transliteration between scripts
- Synchronous client (`Zaban`)
- Asynchronous client (`AsyncZaban`)
- Full type hints with Pydantic models
- Comprehensive error handling
- Auto-detection of source language for translation
- Environment variable support for API key
- Context manager support for both sync and async clients
- Batch translation support with async
- Examples and documentation

### Features
- OpenAI-style API design
- Resource-based endpoint organization
- Intuitive method names and parameters
- Support for file uploads (audio for STT)
- Audio file saving for TTS responses
- Configurable timeout and retries
- Custom base URL support

## [Unreleased]

### Planned
- Streaming support for long audio/text
- Rate limiting utilities
- Caching support
- Retry strategies
- Request/response logging
- Webhook support
- Additional language helpers

