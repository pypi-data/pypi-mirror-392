"""
TalkLabs STT Plugin for LiveKit Agents.
for LiveKit agents using WebSocket streaming.
"""

import asyncio
import json
import logging
import os
from typing import Optional
from urllib.parse import urlencode

import websockets
from livekit import rtc
from livekit.agents import stt, utils

# Import TalkLabs STT SDK
try:
    from talklabs_stt.models import TranscriptionOptions
except ImportError:
    # For backwards compatibility, TranscriptionOptions is optional
    TranscriptionOptions = None

logger = logging.getLogger("livekit_plugins_talklabs.livekit.plugins.talklabs")


class TalkLabsSTT(stt.STT):
    """
    TalkLabs STT plugin for LiveKit Agents with real-time WebSocket streaming.

    Features:
    - VAD integration for natural conversation flow
    - High-quality transcriptions using TalkLabs turbo model
    - Multi-language support

    Example:
        >>> from livekit_stt_class import TalkLabsSTT
        >>>
        >>> stt = TalkLabsSTT(
        ...     api_key="tlk_live_xxxxx",
        ...     language="pt",
        ... )
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        language: str = "pt",
        sample_rate: int = 16000,
        base_url: str = "https://api.talklabs.com.br/api/stt",
    ):
        """
        Initialize TalkLabs STT plugin.

        Args:
            api_key: TalkLabs API key. If not provided, uses TALKLABS_STT_API_KEY env var.
            language: Language code (pt, en, es, fr, de, etc.)
            sample_rate: Audio sample rate in Hz (default: 16000)
            base_url: TalkLabs API base URL
        """
        super().__init__(
            capabilities=stt.STTCapabilities(
                streaming=True,  # Real-time WebSocket streaming
                # Disabled - only FINAL results (optimized for voice agents)
                interim_results=False,
            )
        )

        # Get API key from parameter or environment
        self._api_key = api_key or os.environ.get("TALKLABS_STT_API_KEY")
        if not self._api_key:
            raise ValueError(
                "TalkLabs API key is required. "
                "Provide via api_key parameter or "
                "TALKLABS_STT_API_KEY environment variable."
            )

        self._language = language
        self._sample_rate = sample_rate
        self._base_url = base_url

        logger.info(
            "TalkLabs STT initialized: language=%s, sample_rate=%sHz",
            language, sample_rate
        )

    def stream(
        self,
        *,
        language: Optional[str] = None,
        conn_options=None,
    ) -> "TalkLabsSpeechStream":
        """
        Create a new speech recognition stream.

        Args:
            language: Override default language for this stream
            conn_options: Connection options

        Returns:
            TalkLabsSpeechStream instance
        """
        return TalkLabsSpeechStream(
            stt=self,
            api_key=self._api_key,
            language=language or self._language,
            sample_rate=self._sample_rate,
            base_url=self._base_url,
            conn_options=conn_options,
        )

    async def _recognize_impl(
        self,
        buffer: utils.AudioBuffer,
        *,
        language: Optional[str] = None,
    ) -> stt.SpeechEvent:
        """Not implemented - use stream() method for real-time transcription."""
        raise NotImplementedError(
            "Batch mode not implemented. Use stream() method for real-time transcription."
        )


class TalkLabsSpeechStream(stt.SpeechStream):
    """
    Real-time speech recognition stream using TalkLabs WebSocket API.

    This stream:
    1. Opens persistent WebSocket connection to TalkLabs
    2. Sends audio frames in real-time as they arrive from VAD
    3. Receives transcriptions (interim and final) from TalkLabs
    4. Emits SpeechEvents to LiveKit framework
    """

    _KEEPALIVE_INTERVAL = 20.0  # Send keepalive every 20s
    _FINALIZE_MSG = json.dumps({"type": "Finalize"})

    def __init__(
        self,
        *,
        stt: TalkLabsSTT,
        api_key: str,
        language: str,
        sample_rate: int,
        base_url: str,
        conn_options=None,
    ):
        """
        Initialize speech stream.

        Args:
            stt: Parent STT instance
            api_key: TalkLabs API key
            language: Language for transcription
            sample_rate: Audio sample rate
            base_url: TalkLabs API base URL
            conn_options: Connection options (for LiveKit compatibility)
        """
        super().__init__(stt=stt, sample_rate=sample_rate, conn_options=conn_options)

        self._api_key = api_key
        self._language = language
        self._sample_rate = sample_rate
        self._base_url = base_url

        # WebSocket connection (created in _run)
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

        logger.debug("TalkLabs speech stream created: language=%s", language)

    async def _run(self):
        """
        Main loop: manage WebSocket connection and handle audio/transcription flow.
        """
        try:
            # Connect to TalkLabs WebSocket
            await self._connect()

            # Start parallel tasks
            send_task = asyncio.create_task(self._send_task())
            recv_task = asyncio.create_task(self._recv_task())
            keepalive_task = asyncio.create_task(self._keepalive_task())

            # Wait for tasks to complete
            await asyncio.gather(send_task, recv_task, keepalive_task, return_exceptions=True)

        except Exception as e:
            logger.error("Error in speech stream: %s", e, exc_info=True)
            raise
        finally:
            # Close WebSocket
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:
                    pass
            logger.debug("Speech stream ended")

    async def _connect(self):
        """Establish WebSocket connection to TalkLabs API."""
        # Build WebSocket URL with parameters
        options = TranscriptionOptions(
            language=self._language,
            sample_rate=self._sample_rate,
            interim_results=False,  # Só FINAL results - INTERIM desperdiça recursos
        )

        params = options.to_ws_params()
        query_string = urlencode(params)

        # Convert HTTP URL to WebSocket URL
        ws_base = self._base_url.replace("https://", "wss://")
        ws_base = ws_base.replace("http://", "ws://")
        ws_url = f"{ws_base}/v1/listen?{query_string}"

        logger.info("Connecting to TalkLabs WebSocket: %s", ws_url)

        # Connect (with ping/pong keepalive)
        self._ws = await websockets.connect(
            ws_url,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=5,
            max_size=10 * 1024 * 1024,  # 10MB max message size
        )

        # Authenticate
        await self._ws.send(json.dumps({"xi_api_key": self._api_key}))
        logger.info("TalkLabs WebSocket connected and authenticated")

    async def _send_task(self):
        """Send audio frames to TalkLabs WebSocket in real-time."""
        try:
            # Use AudioByteStream to chunk frames into consistent sizes
            # (1 second chunks for optimal latency/quality balance)
            # Benchmark: 1s = 7.43s (best), 3s = 7.43s, 4s = 12.43s,
            # 5s = 10.42s
            # 1000ms (1 second) chunks - OPTIMAL
            samples_1sec = self._sample_rate * 1
            audio_bstream = utils.audio.AudioByteStream(
                sample_rate=self._sample_rate,
                num_channels=1,  # Mono
                samples_per_channel=samples_1sec,
            )

            has_ended = False
            async for data in self._input_ch:
                frames: list[rtc.AudioFrame] = []

                if isinstance(data, rtc.AudioFrame):
                    # VAD sending audio - chunk it and send
                    frames.extend(audio_bstream.write(data.data.tobytes()))

                elif isinstance(data, self._FlushSentinel):
                    # VAD detected end of speech - flush remaining audio and finalize
                    frames.extend(audio_bstream.flush())
                    has_ended = True

                # Send all frames
                for frame in frames:
                    await self._ws.send(frame.data.tobytes())
                    logger.debug("Sent audio chunk: %s bytes", len(frame.data))

                # Send Finalize ONCE after all frames (not inside loop!)
                if has_ended:
                    await self._ws.send(self._FINALIZE_MSG)
                    logger.info("Sent Finalize message (end of utterance)")
                    has_ended = False

        except Exception as e:
            logger.error("Error in send task: %s", e, exc_info=True)
            raise

    async def _recv_task(self):
        """Receive transcriptions from TalkLabs WebSocket."""
        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "Metadata":
                        # Metadata message - log and ignore
                        logger.debug("Received Metadata from TalkLabs")

                    elif msg_type == "Results":
                        # Transcription result!
                        await self._handle_transcription(data)

                    elif msg_type == "Error":
                        # Error from TalkLabs
                        error_msg = data.get("error", data.get("message", "Unknown error"))
                        logger.error("TalkLabs error: %s", error_msg)

                    else:
                        logger.warning("Unknown message type: %s", msg_type)

                except json.JSONDecodeError:
                    logger.warning("Failed to parse message: %s", message)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Error in receive task: %s", e, exc_info=True)

    async def _handle_transcription(self, data: dict):
        """
        Process transcription result from TalkLabs and emit SpeechEvent.

        Args:
            data: TalkLabs transcription result
        """
        try:
            # Extract transcription
            alternatives = data.get("channel", {}).get("alternatives", [])
            if not alternatives:
                logger.warning("No alternatives in TalkLabs response")
                return

            transcript = alternatives[0].get("transcript", "")
            confidence = alternatives[0].get("confidence", 0.0)
            is_final = data.get("is_final", False)

            if not transcript.strip():
                logger.debug("Empty transcript, skipping")
                return

            # Log with color (green for transcriptions)
            status = "FINAL" if is_final else "INTERIM"
            # Only log FINAL transcripts to reduce noise (INTERIM são provisórios)
            if is_final:
                logger.info(
                    "\033[92m%s: '%s' (confidence: %.2f%%)\033[0m",
                    status, transcript, confidence * 100
                )
            else:
                logger.debug("%s: '%s' (confidence: %.2f%%)", status, transcript, confidence * 100)

            # Create SpeechEvent
            event_type = (
                stt.SpeechEventType.FINAL_TRANSCRIPT
                if is_final
                else stt.SpeechEventType.INTERIM_TRANSCRIPT
            )

            event = stt.SpeechEvent(
                type=event_type,
                alternatives=[
                    stt.SpeechData(
                        language=self._language,
                        text=transcript,
                        start_time=0.0,  # TalkLabs doesn't provide timestamps yet
                        end_time=0.0,
                        confidence=confidence,
                    )
                ],
            )

            # Emit event to LiveKit framework
            self._event_ch.send_nowait(event)

        except Exception as e:
            logger.error("Error handling transcription: %s", e, exc_info=True)

    async def _keepalive_task(self):
        """Send periodic keepalive messages to maintain WebSocket connection."""
        try:
            while True:
                await asyncio.sleep(self._KEEPALIVE_INTERVAL)
                # Websockets library handles ping/pong automatically
                # This task just keeps the loop alive
        except asyncio.CancelledError:
            pass
