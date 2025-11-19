# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-18

### Added
- Initial release of Realtime ASR SDK
- WebSocket client implementation for real-time speech transcription
- Support for multiple audio formats (8kHz - 44.1kHz PCM)
- Audio stream handler for microphone capture
- Event-driven architecture with callbacks
- Multiple language support (auto-detect, en, zh, ja, ko, es, fr, de, etc.)
- Word-level timestamps support
- Commit strategies: VAD (Voice Activity Detection) and Manual
- Comprehensive error handling
- Example scripts:
  - `simple_example.py` - Basic usage demonstration
  - `stream_from_mic.py` - Full-featured microphone streaming
  - `send_audio_file.py` - Send pre-recorded audio files
- Full documentation in README.md
- Type hints and dataclass-based message types

### Features
- `RealtimeASRClient` - Main WebSocket client for ASR communication
- `AudioStream` - Audio capture and processing
- `AudioFormat` - Support for multiple sample rates
- `CommitStrategy` - VAD and manual commit modes
- Message types: SessionStarted, PartialTranscript, CommittedTranscript, Error
- Connection management with automatic reconnection handling
- Session management with unique session IDs

### Dependencies
- `websocket-client>=1.6.0` - WebSocket communication
- `numpy>=1.24.0` - Audio data processing
- `PyAudio>=0.2.13` - Microphone capture (optional)

[0.1.0]: https://github.com/inccleo/realtime-asr-sdk/releases/tag/v0.1.0

