"""
Utility functions for the Realtime ASR SDK
"""

from typing import Dict, Any
import json


def format_transcript_with_timestamps(text: str, words: list) -> str:
    """
    Format transcript with word-level timestamps

    Args:
        text: Full transcript text
        words: List of word timestamps

    Returns:
        Formatted string with timestamps
    """
    if not words:
        return text

    lines = [f"Transcript: {text}", ""]
    lines.append("Word-level timestamps:")
    lines.append("-" * 50)

    for word_data in words:
        word = word_data.get("word", "")
        start = word_data.get("start", 0.0)
        end = word_data.get("end", 0.0)
        duration = end - start
        lines.append(f"{start:8.3f}s - {end:8.3f}s ({duration:6.3f}s): {word}")

    return "\n".join(lines)


def message_to_dict(message) -> Dict[str, Any]:
    """
    Convert message object to dictionary

    Args:
        message: Message object

    Returns:
        Dictionary representation
    """
    if hasattr(message, "raw_data"):
        return message.raw_data
    return {}


def message_to_json(message, indent: int = 2) -> str:
    """
    Convert message object to JSON string

    Args:
        message: Message object
        indent: JSON indentation

    Returns:
        JSON string
    """
    return json.dumps(message_to_dict(message), indent=indent)


def calculate_audio_duration(audio_data: bytes, sample_rate: int, sample_width: int = 2) -> float:
    """
    Calculate duration of audio data in seconds

    Args:
        audio_data: Raw audio bytes
        sample_rate: Sample rate in Hz
        sample_width: Sample width in bytes (default: 2 for 16-bit)

    Returns:
        Duration in seconds
    """
    num_samples = len(audio_data) // sample_width
    return num_samples / sample_rate


def validate_audio_format(sample_rate: int, sample_width: int, channels: int) -> bool:
    """
    Validate audio format parameters

    Args:
        sample_rate: Sample rate in Hz
        sample_width: Sample width in bytes
        channels: Number of channels

    Returns:
        True if valid, False otherwise
    """
    valid_rates = [8000, 16000, 22050, 24000, 44100]
    valid_widths = [1, 2]  # 8-bit, 16-bit
    valid_channels = [1, 2]  # mono, stereo

    return (
        sample_rate in valid_rates
        and sample_width in valid_widths
        and channels in valid_channels
    )
