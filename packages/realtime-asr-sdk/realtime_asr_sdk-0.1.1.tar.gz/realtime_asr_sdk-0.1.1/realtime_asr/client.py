"""
Real-time ASR WebSocket client
"""

import json
import logging
import threading
from typing import Optional, Callable, Dict, Any
from urllib.parse import urlencode

try:
    import websocket
except ImportError:
    websocket = None

from .types import (
    AudioFormat,
    CommitStrategy,
    TranscriptionMessage,
    SessionStartedMessage,
    PartialTranscriptMessage,
    CommittedTranscriptMessage,
    CommittedTranscriptWithTimestampsMessage,
    ErrorMessage,
)
from .audio import pcm_to_base64


logger = logging.getLogger(__name__)


class RealtimeASRClient:
    """
    Real-time ASR WebSocket client

    Example:
        ```python
        client = RealtimeASRClient(
            ws_url="ws://localhost:8081/asr/realtime",
            api_key="your-api-key",
            model_id="echo_v1_realtime"
        )

        def on_transcript(message):
            print(f"Transcript: {message.text}")

        client.on_partial_transcript = on_transcript
        client.connect()

        # Send audio data
        client.send_audio(audio_bytes)

        client.disconnect()
        ```
    """

    def __init__(
        self,
        ws_url: str,
        api_key: str,
        model_id: str = "echo_v1_realtime",
        language: Optional[str] = None,
        audio_format: AudioFormat = AudioFormat.PCM_16000,
        commit_mode: CommitStrategy = CommitStrategy.VAD,
        word_timestamps: bool = True,
    ):
        """
        Initialize WebSocket client

        Args:
            ws_url: WebSocket URL (e.g., "ws://localhost:8081/asr/realtime")
            api_key: API key for authentication
            model_id: Model ID to use (e.g., "echo_v1_realtime", "lexis_v1")
            language: Language code (e.g., "en", "zh", "ja") or None for auto-detect
            audio_format: Audio format specification
            commit_mode: Commit strategy (VAD or manual)
            word_timestamps: Whether to request word-level timestamps
        """
        if websocket is None:
            raise ImportError(
                "websocket-client is required. "
                "Install it with: pip install websocket-client"
            )

        self.ws_url = ws_url
        self.api_key = api_key
        self.model_id = model_id
        self.language = language
        self.audio_format = audio_format
        self.commit_mode = commit_mode
        self.word_timestamps = word_timestamps

        self._ws: Optional[websocket.WebSocketApp] = None
        self._ws_thread: Optional[threading.Thread] = None
        self._is_connected = False
        self._session_id: Optional[str] = None

        # Event callbacks
        self.on_session_started: Optional[Callable[[SessionStartedMessage], None]] = None
        self.on_partial_transcript: Optional[Callable[[PartialTranscriptMessage], None]] = None
        self.on_committed_transcript: Optional[Callable[[CommittedTranscriptMessage], None]] = None
        self.on_committed_transcript_with_timestamps: Optional[Callable[[CommittedTranscriptWithTimestampsMessage], None]] = None
        self.on_error: Optional[Callable[[ErrorMessage], None]] = None
        self.on_message: Optional[Callable[[TranscriptionMessage], None]] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[int, str], None]] = None

    def _build_url(self) -> str:
        """Build WebSocket URL with query parameters"""
        params = {
            "api-key": self.api_key,
            "model_id": self.model_id,
            "audio_format": self.audio_format.value,
            "commit_mode": self.commit_mode.value,
            "word_timestamps": "true" if self.word_timestamps else "false",
        }

        if self.language:
            params["language"] = self.language

        return f"{self.ws_url}?{urlencode(params)}"

    def connect(self, timeout: float = 10.0) -> None:
        """
        Connect to WebSocket server

        Args:
            timeout: Connection timeout in seconds
        """
        if self._is_connected:
            logger.warning("Already connected")
            return

        url = self._build_url()
        logger.info(f"Connecting to {self.ws_url}")

        self._ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        # Run WebSocket in separate thread
        self._ws_thread = threading.Thread(
            target=self._ws.run_forever,
            daemon=True
        )
        self._ws_thread.start()

        # Wait for connection
        wait_time = 0.0
        wait_interval = 0.1
        while not self._is_connected and wait_time < timeout:
            threading.Event().wait(wait_interval)
            wait_time += wait_interval

        if not self._is_connected:
            raise TimeoutError(f"Failed to connect within {timeout} seconds")

    def disconnect(self) -> None:
        """Disconnect from WebSocket server"""
        if not self._is_connected:
            return

        logger.info("Disconnecting...")
        self._is_connected = False

        if self._ws:
            self._ws.close()
            self._ws = None

        if self._ws_thread:
            self._ws_thread.join(timeout=2.0)
            self._ws_thread = None

    def send_audio(
        self,
        audio_data: bytes,
        commit: bool = False
    ) -> None:
        """
        Send audio chunk to server

        Args:
            audio_data: Raw PCM audio bytes (16-bit signed integers)
            commit: Whether to commit this chunk (for manual commit mode)
        """
        if not self._is_connected or not self._ws:
            raise RuntimeError("Not connected to server")

        # Convert to base64
        audio_base64 = pcm_to_base64(audio_data)

        # Build message
        message = {
            "message_type": "input_audio_chunk",
            "audio_base_64": audio_base64,
            "commit": commit,
            "sample_rate": self.audio_format.sample_rate,
        }

        # Send as JSON
        self._ws.send(json.dumps(message))

    @property
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self._is_connected

    @property
    def session_id(self) -> Optional[str]:
        """Get current session ID"""
        return self._session_id

    # WebSocket event handlers

    def _on_open(self, ws) -> None:
        """Handle WebSocket connection opened"""
        logger.info("WebSocket connection established")
        self._is_connected = True

        if self.on_connected:
            try:
                self.on_connected()
            except Exception as e:
                logger.error(f"Error in on_connected callback: {e}")

    def _on_message(self, ws, message: str) -> None:
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_obj = TranscriptionMessage.from_dict(data)

            # Call general message handler
            if self.on_message:
                try:
                    self.on_message(msg_obj)
                except Exception as e:
                    logger.error(f"Error in on_message callback: {e}")

            # Call specific handlers
            if isinstance(msg_obj, SessionStartedMessage):
                self._session_id = msg_obj.session_id
                logger.info(f"Session started: {self._session_id}")
                if self.on_session_started:
                    try:
                        self.on_session_started(msg_obj)
                    except Exception as e:
                        logger.error(f"Error in on_session_started callback: {e}")

            elif isinstance(msg_obj, PartialTranscriptMessage):
                if self.on_partial_transcript:
                    try:
                        self.on_partial_transcript(msg_obj)
                    except Exception as e:
                        logger.error(f"Error in on_partial_transcript callback: {e}")

            elif isinstance(msg_obj, CommittedTranscriptMessage):
                if self.on_committed_transcript:
                    try:
                        self.on_committed_transcript(msg_obj)
                    except Exception as e:
                        logger.error(f"Error in on_committed_transcript callback: {e}")

            elif isinstance(msg_obj, CommittedTranscriptWithTimestampsMessage):
                if self.on_committed_transcript_with_timestamps:
                    try:
                        self.on_committed_transcript_with_timestamps(msg_obj)
                    except Exception as e:
                        logger.error(f"Error in on_committed_transcript_with_timestamps callback: {e}")

            elif isinstance(msg_obj, ErrorMessage):
                logger.error(f"Received error: {msg_obj.error}")
                if self.on_error:
                    try:
                        self.on_error(msg_obj)
                    except Exception as e:
                        logger.error(f"Error in on_error callback: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def _on_error(self, ws, error) -> None:
        """Handle WebSocket error"""
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """Handle WebSocket connection closed"""
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        self._is_connected = False
        self._session_id = None

        if self.on_disconnected:
            try:
                self.on_disconnected(close_status_code or 0, close_msg or "")
            except Exception as e:
                logger.error(f"Error in on_disconnected callback: {e}")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
