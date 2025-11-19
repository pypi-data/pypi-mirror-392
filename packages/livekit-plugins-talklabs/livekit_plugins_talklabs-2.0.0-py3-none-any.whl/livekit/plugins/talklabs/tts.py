"""TalkLabs TTS Plugin for LiveKit Agents."""

import asyncio
import logging

from livekit.agents import tts as lk_tts
from livekit.agents import utils
from livekit.agents.tts.tts import (
    APIConnectOptions,
    ChunkedStream,
    DEFAULT_API_CONNECT_OPTIONS,
    SynthesizeStream,
)
from talklabs import TalkLabsClient

logger = logging.getLogger("livekit.plugins.talklabs")


class TalkLabsTTS(lk_tts.TTS):
    """
    Adaptador TalkLabs para LiveKit Agents com sessão persistente.

    Usa client.create_session() do SDK TalkLabs para manter uma conexão
    WebSocket persistente e reutilizá-la entre múltiplas sínteses.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.talklabs.com.br",
        voice: str = "pt-br/adam_rocha",
        language: str = "pt",
        speed: float = 1.0,
        sample_rate: int = 24000,
        num_channels: int = 1,
        ping_interval: float = 20.0,
        ping_timeout: float = 20.0,
    ):
        super().__init__(
            capabilities=lk_tts.TTSCapabilities(streaming=True),
            sample_rate=sample_rate,
            num_channels=num_channels,
        )
        self.voice = voice
        self.language = language
        self.speed = speed
        self.api_key = api_key
        self.base_url = base_url
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        # Client e sessão persistente (criados no primeiro uso)
        self._client = None
        self._session = None
        self._session_lock = asyncio.Lock()  # Lock para sincronizar criação da sessão

        logger.info("[TalkLabsTTS] Initialized with voice=%s", voice)

    async def _ensure_session(self):
        """Garante que existe uma sessão persistente ativa."""
        # Usa lock para evitar criar múltiplas sessões simultaneamente
        async with self._session_lock:
            if self._session is None:
                logger.info("[TalkLabsTTS] Creating persistent session...")

                # Cria cliente
                if self._client is None:
                    self._client = TalkLabsClient(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )

                # Cria sessão persistente usando SDK TalkLabs
                self._session = await self._client.create_session(
                    voice=self.voice,
                    language=self.language,
                    speed=self.speed,
                    ping_interval=self.ping_interval,
                    ping_timeout=self.ping_timeout,
                )

                logger.info("[TalkLabsTTS] Persistent session created!")
            else:
                logger.info("[TalkLabsTTS] Reusing existing session")

        return self._session

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS
    ) -> ChunkedStream:
        """Método síncrono requerido pela interface TTS."""
        return ChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options
        )

    def stream(self, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS):
        """Create a new TTS streaming session."""
        return TalkLabsStream(tts=self, conn_options=conn_options)

    async def aclose(self):
        """Fecha a sessão persistente."""
        if self._session:
            logger.info("[TalkLabsTTS] Closing persistent session...")
            await self._session.close()
            self._session = None
            logger.info("[TalkLabsTTS] Session closed")


class TalkLabsStream(SynthesizeStream):
    """
    Streaming TalkLabs TTS usando sessão persistente do SDK.

    Reutiliza a mesma sessão WebSocket para todas as sínteses,
    reduzindo latência e overhead de conexão.
    """

    def __init__(self, *, tts: TalkLabsTTS, conn_options: APIConnectOptions):
        super().__init__(tts=tts, conn_options=conn_options)
        self._tts = tts

    async def _run(self, output_emitter):
        request_id = utils.shortuuid()

        # Inicializa output_emitter
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            # TalkLabs retorna raw PCM16 (use "audio/wav" se servidor
            # mudar para WAV com header RIFF)
            mime_type="audio/pcm",
            stream=True,
        )

        # Garante que temos uma sessão persistente ativa
        session = await self._tts._ensure_session()

        try:
            # Processa texto conforme chega do input channel
            text_buffer = []

            async for data in self._input_ch:
                if isinstance(data, self._FlushSentinel):
                    # Flush: sintetiza o texto acumulado
                    if text_buffer:
                        text = "".join(text_buffer).strip()
                        if text:
                            await self._synthesize_segment(text, session, output_emitter)
                        text_buffer = []
                    continue

                if isinstance(data, str):
                    text_buffer.append(data)

            # Processa qualquer texto restante no buffer
            if text_buffer:
                text = "".join(text_buffer).strip()
                if text:
                    await self._synthesize_segment(text, session, output_emitter)

        except Exception as e:
            logger.error("[TalkLabsStream] Erro fatal: %s", e)
            raise
        finally:
            output_emitter.flush()

    async def _synthesize_segment(self, text: str, session, output_emitter):
        """Sintetiza um segmento de texto e envia para o output"""
        segment_id = utils.shortuuid()

        # Log em VERDE (resposta da LLM)
        logger.info("\033[92m[TalkLabsStream] 🤖 LLM RESPONDE: '%s'\033[0m", text)

        output_emitter.start_segment(segment_id=segment_id)

        try:
            chunk_count = 0
            async for chunk in session.stream_text(text):
                chunk_count += 1
                logger.debug("[TalkLabsStream] Chunk %s: %s bytes", chunk_count, len(chunk))
                output_emitter.push(chunk)

            logger.info("[TalkLabsStream] Synthesis complete (%s chunks)", chunk_count)

        except Exception as e:
            logger.error("[TalkLabsStream] Erro no streaming: %s", e)
            raise
        finally:
            output_emitter.end_segment()
