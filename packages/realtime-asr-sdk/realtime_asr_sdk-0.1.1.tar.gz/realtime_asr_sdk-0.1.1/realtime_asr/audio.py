"""
Audio capture and processing utilities
"""

import base64
import struct
import threading
from typing import Optional, Callable
import numpy as np

try:
    import pyaudio
except ImportError:
    pyaudio = None

from .types import AudioFormat


class AudioStream:
    """
    Audio stream handler for capturing and processing microphone input
    """

    def __init__(
        self,
        audio_format: AudioFormat = AudioFormat.PCM_16000,
        chunk_size: int = 4096,
        channels: int = 1,
    ):
        """
        Initialize audio stream

        Args:
            audio_format: Audio format (determines sample rate)
            chunk_size: Number of frames per buffer
            channels: Number of audio channels (1 for mono)
        """
        if pyaudio is None:
            raise ImportError(
                "pyaudio is required for audio streaming. "
                "Install it with: pip install pyaudio"
            )

        self.audio_format = audio_format
        self.sample_rate = audio_format.sample_rate
        self.chunk_size = chunk_size
        self.channels = channels

        self._pyaudio = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None
        self._callback: Optional[Callable[[bytes], None]] = None
        self._is_recording = False
        self._thread: Optional[threading.Thread] = None

    def start(self, callback: Callable[[bytes], None]) -> None:
        """
        Start audio capture

        Args:
            callback: Function to call with audio chunks (raw PCM bytes)
        """
        if self._is_recording:
            raise RuntimeError("Audio stream is already recording")

        self._callback = callback
        self._is_recording = True

        # Open audio stream
        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16,  # 16-bit PCM
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._audio_callback,
        )

        self._stream.start_stream()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio stream callback"""
        if self._callback and self._is_recording:
            self._callback(in_data)
        return (None, pyaudio.paContinue)

    def stop(self) -> None:
        """Stop audio capture"""
        if not self._is_recording:
            return

        self._is_recording = False

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        self._callback = None

    def close(self) -> None:
        """Close and cleanup resources"""
        self.stop()
        if self._pyaudio:
            self._pyaudio.terminate()
            self._pyaudio = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def pcm_to_base64(pcm_data: bytes) -> str:
    """
    Convert PCM audio data to base64 string

    Args:
        pcm_data: Raw PCM audio bytes (16-bit signed integers)

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(pcm_data).decode('utf-8')


def normalize_audio(pcm_data: bytes) -> bytes:
    """
    Normalize audio data to ensure proper range

    Args:
        pcm_data: Raw PCM audio bytes (16-bit signed integers)

    Returns:
        Normalized PCM audio bytes
    """
    # Convert bytes to numpy array
    audio_array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32)

    # Normalize to [-1.0, 1.0]
    audio_array = audio_array / 32768.0

    # Clip to valid range
    audio_array = np.clip(audio_array, -1.0, 1.0)

    # Convert back to 16-bit PCM
    audio_array = (audio_array * 32767).astype(np.int16)

    return audio_array.tobytes()


def convert_sample_rate(
    pcm_data: bytes,
    from_rate: int,
    to_rate: int,
    channels: int = 1
) -> bytes:
    """
    Convert audio sample rate (simple linear interpolation)

    Args:
        pcm_data: Raw PCM audio bytes
        from_rate: Source sample rate
        to_rate: Target sample rate
        channels: Number of channels

    Returns:
        Resampled PCM audio bytes
    """
    if from_rate == to_rate:
        return pcm_data

    # Convert to numpy array
    audio_array = np.frombuffer(pcm_data, dtype=np.int16)

    # Calculate resampling factor
    ratio = to_rate / from_rate
    new_length = int(len(audio_array) * ratio)

    # Simple linear interpolation
    indices = np.arange(new_length) / ratio
    resampled = np.interp(
        indices,
        np.arange(len(audio_array)),
        audio_array
    ).astype(np.int16)

    return resampled.tobytes()
