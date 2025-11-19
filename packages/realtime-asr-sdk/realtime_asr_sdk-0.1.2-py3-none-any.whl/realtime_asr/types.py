"""
Type definitions for real-time ASR messages
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class MessageType(Enum):
    """WebSocket message types"""
    SESSION_STARTED = "session_started"
    PARTIAL_TRANSCRIPT = "partial_transcript"
    COMMITTED_TRANSCRIPT = "committed_transcript"
    COMMITTED_TRANSCRIPT_WITH_TIMESTAMPS = "committed_transcript_with_timestamps"
    INPUT_AUDIO_CHUNK = "input_audio_chunk"
    ERROR = "error"
    AUTH_ERROR = "auth_error"
    QUOTA_EXCEEDED_ERROR = "quota_exceeded_error"
    UNACCEPTED_TERMS = "unaccepted_terms"


class AudioFormat(Enum):
    """Supported audio formats"""
    PCM_8000 = "pcm_8000"
    PCM_16000 = "pcm_16000"
    PCM_22050 = "pcm_22050"
    PCM_24000 = "pcm_24000"
    PCM_44100 = "pcm_44100"

    @property
    def sample_rate(self) -> int:
        """Extract sample rate from format string"""
        return int(self.value.split('_')[1])


class CommitStrategy(Enum):
    """Commit strategy for transcription"""
    VAD = "vad"  # Voice Activity Detection (automatic)
    MANUAL = "manual"  # Manual commit


@dataclass
class WordTimestamp:
    """Word-level timestamp information"""
    word: str
    start: float
    end: float


@dataclass
class TranscriptionMessage:
    """Base class for transcription messages"""
    message_type: str
    raw_data: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptionMessage':
        """Create appropriate message subclass based on message_type"""
        message_type = data.get("message_type")

        if message_type == MessageType.SESSION_STARTED.value:
            return SessionStartedMessage.from_dict(data)
        elif message_type == MessageType.PARTIAL_TRANSCRIPT.value:
            return PartialTranscriptMessage.from_dict(data)
        elif message_type == MessageType.COMMITTED_TRANSCRIPT.value:
            return CommittedTranscriptMessage.from_dict(data)
        elif message_type == MessageType.COMMITTED_TRANSCRIPT_WITH_TIMESTAMPS.value:
            return CommittedTranscriptWithTimestampsMessage.from_dict(data)
        elif message_type in [MessageType.ERROR.value, MessageType.AUTH_ERROR.value,
                              MessageType.QUOTA_EXCEEDED_ERROR.value, MessageType.UNACCEPTED_TERMS.value]:
            return ErrorMessage.from_dict(data)
        else:
            return cls(message_type=message_type, raw_data=data)


@dataclass
class SessionStartedMessage(TranscriptionMessage):
    """Session started message"""
    session_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionStartedMessage':
        return cls(
            message_type=data.get("message_type", ""),
            raw_data=data,
            session_id=data.get("session_id")
        )


@dataclass
class PartialTranscriptMessage(TranscriptionMessage):
    """Partial (interim) transcript message"""
    text: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PartialTranscriptMessage':
        return cls(
            message_type=data.get("message_type", ""),
            raw_data=data,
            text=data.get("text", "")
        )


@dataclass
class CommittedTranscriptMessage(TranscriptionMessage):
    """Committed (final) transcript message"""
    text: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommittedTranscriptMessage':
        return cls(
            message_type=data.get("message_type", ""),
            raw_data=data,
            text=data.get("text", "")
        )


@dataclass
class CommittedTranscriptWithTimestampsMessage(TranscriptionMessage):
    """Committed transcript with word-level timestamps"""
    text: str = ""
    words: List[WordTimestamp] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommittedTranscriptWithTimestampsMessage':
        words_data = data.get("words", [])
        words = [
            WordTimestamp(
                word=w.get("word", ""),
                start=w.get("start", 0.0),
                end=w.get("end", 0.0)
            )
            for w in words_data
        ]

        return cls(
            message_type=data.get("message_type", ""),
            raw_data=data,
            text=data.get("text", ""),
            words=words
        )


@dataclass
class ErrorMessage(TranscriptionMessage):
    """Error message"""
    error: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorMessage':
        return cls(
            message_type=data.get("message_type", ""),
            raw_data=data,
            error=data.get("error", "") or str(data)
        )
