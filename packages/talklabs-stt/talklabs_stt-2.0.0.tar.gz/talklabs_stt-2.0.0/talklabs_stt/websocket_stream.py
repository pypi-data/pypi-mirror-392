"""
TalkLabs STT SDK - WebSocket Streamer

WebSocket streaming transcription logic with persistent connections.

Author: Francisco Lima
License: MIT
"""

import asyncio
import json
import logging
from typing import Optional, Callable
from urllib.parse import urlencode
import websockets

from .models import TranscriptionOptions
from .validators import validate_file_exists
from .audio_processor import prepare_audio_for_streaming
from .decorators import handle_errors

logger = logging.getLogger(__name__)


class WebSocketStreamer:
    """
    Cliente WebSocket para transcrição em tempo real.

    Características:
    - Conexão persistente automática
    - Reutilização de conexão entre múltiplas transcrições
    - Ping/pong keep-alive (20s)
    - Gestão segura de lifecycle
    """

    def __init__(self, api_key: str, base_url: str):
        """
        Inicializa o streamer WebSocket.

        Args:
            api_key: Chave de API
            base_url: URL base da API (HTTP/HTTPS)
        """
        self.api_key = api_key
        self.base_url = base_url

        # Conexão persistente
        self._ws = None
        self._ws_params = None

    async def stream(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions] = None,
        on_transcript: Optional[Callable[[dict], None]] = None,
        on_metadata: Optional[Callable[[dict], None]] = None,
        chunk_size: int = 800000,
        **kwargs
    ):
        """
        Transcreve áudio via WebSocket com reconexão automática.

        Primeira chamada: Abre conexão
        Chamadas seguintes: Reutiliza conexão automaticamente
        Se servidor fechar conexão: Reconecta e retenta automaticamente (1x)
        Para fechar: Chame close() quando terminar

        Args:
            audio_path: Caminho para o arquivo de áudio
            options: Opções (usadas apenas na primeira chamada)
            on_transcript: Callback para cada transcrição recebida
            on_metadata: Callback para metadata da sessão
            chunk_size: Tamanho dos chunks em bytes (default: 800000 = 25s @ 16kHz)
            **kwargs: Parâmetros adicionais (model, language, etc.)

        Raises:
            FileNotFoundError: Se o arquivo não existir
            websockets.exceptions.WebSocketException: Erro de conexão
        """
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                await self._stream_internal(
                    audio_path, options, on_transcript, on_metadata, chunk_size, **kwargs
                )
                # Sucesso - sai do loop
                return
            except websockets.exceptions.ConnectionClosed as e:
                if attempt < max_retries:
                    logger.info(
                        f"[TalkLabs STT] 🔄 Conexão fechada (code {e.code}) - "
                        f"Tentando novamente ({attempt + 1}/{max_retries})..."
                    )
                    self._ws = None  # Força reconexão
                    await asyncio.sleep(0.5)  # Pequeno delay
                else:
                    logger.warning(
                        f"[TalkLabs STT] ❌ Falha após {max_retries + 1} tentativas"
                    )
                    raise

    async def _stream_internal(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions],
        on_transcript: Optional[Callable[[dict], None]],
        on_metadata: Optional[Callable[[dict], None]],
        chunk_size: int,
        **kwargs
    ):
        """Lógica interna de streaming (usada pelo retry)."""
        # Abre conexão se necessário
        await self._ensure_connected(audio_path, options, **kwargs)

        # Valida arquivo
        validate_file_exists(audio_path)

        # Prepara áudio
        logger.info(f"[TalkLabs STT] 📂 Preparando áudio: {audio_path}")

        target_sample_rate = 16000
        if self._ws_params:
            target_sample_rate = int(self._ws_params.get("sample_rate", 16000))

        audio_bytes, actual_sample_rate = prepare_audio_for_streaming(
            audio_path, target_sample_rate
        )

        logger.info(f"[TalkLabs STT] 🎵 Enviando: {len(audio_bytes)} bytes, {actual_sample_rate}Hz")

        # Event para sinalizar quando receber resultado final
        final_received = asyncio.Event()

        try:
            # Tasks paralelas
            send_task = asyncio.create_task(
                self._send_audio(audio_bytes, chunk_size)
            )
            receive_task = asyncio.create_task(
                self._receive_transcripts(on_transcript, on_metadata, final_received)
            )

            # Aguarda envio terminar
            await send_task

            # Aguarda receber pelo menos UM resultado final
            try:
                await asyncio.wait_for(final_received.wait(), timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("[TalkLabs STT] ⚠️  Timeout aguardando primeiro resultado final")

            # Aguarda mais resultados
            try:
                await asyncio.wait_for(receive_task, timeout=60.0)
            except asyncio.TimeoutError:
                logger.warning("[TalkLabs STT] ⚠️  Timeout aguardando conclusão")
                if not receive_task.done():
                    receive_task.cancel()
                    try:
                        await receive_task
                    except asyncio.CancelledError:
                        pass

            logger.info("[TalkLabs STT] ✅ Transcrição concluída")

        except websockets.exceptions.ConnectionClosed:
            # Propaga para o retry handler em stream()
            self._ws = None
            raise
        except Exception as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro: {e}")
            raise

    async def _ensure_connected(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions],
        **kwargs
    ):
        """
        Garante que há uma conexão WebSocket ativa.

        Se não há conexão OU conexão está fechada, abre uma nova.
        Se já há conexão ativa, apenas loga reutilização.
        """
        # Verifica se precisa (re)conectar
        needs_reconnect = False

        if not self._ws:
            needs_reconnect = True
            reason = "Primeira conexão"
        else:
            # Verifica se a conexão está fechada
            try:
                # Verifica múltiplos indicadores de conexão fechada
                is_closed = getattr(self._ws, 'closed', True)
                close_code = getattr(self._ws, 'close_code', None)

                # Se closed=True ou há close_code, a conexão foi fechada
                if is_closed or close_code is not None:
                    needs_reconnect = True
                    reason = f"Reconexão (conexão fechada: code {close_code})"
                    logger.info(
                        "[TalkLabs STT] 🔍 Detectou conexão fechada: "
                        "closed=%s, code=%s", is_closed, close_code
                    )
                    self._ws = None
            except Exception as e:
                # Se houver qualquer erro, assume que precisa reconectar
                needs_reconnect = True
                reason = f"Reconexão (erro ao verificar estado: {e})"
                self._ws = None

        if needs_reconnect:
            # Prepara opções
            if options is None:
                options = TranscriptionOptions()

            for key, value in kwargs.items():
                if hasattr(options, key):
                    setattr(options, key, value)

            # Força modelo 'turbo' - outros valores são ignorados
            options.model = "turbo"

            # Prepara áudio para detectar sample_rate (apenas na primeira vez)
            if not self._ws_params:
                _, actual_sample_rate = prepare_audio_for_streaming(audio_path, options.sample_rate)
                options.sample_rate = actual_sample_rate
                self._ws_params = options.to_ws_params()

            # Monta URL
            base_ws_url = self.base_url.replace("https://", "wss://").replace("http://", "ws://")
            query_string = urlencode(self._ws_params)
            ws_url = f"{base_ws_url}/v1/listen?{query_string}"

            logger.info(f"[TalkLabs STT] 🔌 {reason} - Abrindo WebSocket...")

            # Conecta (SEM async with - gerenciamos manualmente)
            self._ws = await websockets.connect(
                ws_url,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=5,
                max_size=10 * 1024 * 1024
            )

            # Autenticação
            await self._ws.send(json.dumps({"xi_api_key": self.api_key}))
            logger.info("[TalkLabs STT] ✅ Conexão WebSocket estabelecida")
        else:
            logger.info("[TalkLabs STT] ♻️  Reutilizando conexão WebSocket existente")

    @handle_errors(logger)
    async def _send_audio(self, audio_bytes: bytes, chunk_size: int):
        """
        Envia chunks de áudio para WebSocket.

        Args:
            audio_bytes: Bytes de áudio PCM
            chunk_size: Tamanho de cada chunk
        """
        total_chunks = len(audio_bytes) // chunk_size + 1
        logger.info(
            f"[TalkLabs STT] 📦 Enviando {total_chunks} chunks "
            f"({len(audio_bytes)} bytes)"
        )

        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            await self._ws.send(chunk)
            # Pequeno yield para não bloquear event loop
            await asyncio.sleep(0)

        # Finaliza (indica fim do áudio, mas NÃO fecha conexão)
        await self._ws.send(json.dumps({"type": "Finalize"}))
        logger.info("[TalkLabs STT] 📤 Áudio enviado completamente")

        # NÃO envia CloseStream - mantém conexão aberta para reutilizar!

    async def _receive_transcripts(
        self,
        on_transcript: Optional[Callable],
        on_metadata: Optional[Callable],
        final_received: asyncio.Event
    ):
        """
        Recebe transcrições do WebSocket.

        Args:
            on_transcript: Callback para resultados
            on_metadata: Callback para metadata
            final_received: Event para sinalizar resultado final
        """
        try:
            async for message in self._ws:
                data = json.loads(message)

                # Log tipo de mensagem
                logger.debug(
                    "[TalkLabs STT] 📨 Mensagem recebida: type=%s",
                    data.get('type', 'UNKNOWN')
                )

                # Metadata
                if data.get("type") == "Metadata":
                    logger.debug("[TalkLabs STT] 📋 Metadata recebida")
                    if on_metadata:
                        on_metadata(data)

                # Resultados
                elif data.get("type") == "Results":
                    alternatives = data.get("channel", {}).get("alternatives", [{}])
                    transcript = alternatives[0].get("transcript", "")
                    is_final = data.get("is_final", False)

                    status = "FINAL" if is_final else "INTERIM"
                    logger.info(f"[TalkLabs STT] {status}: {transcript}")

                    if on_transcript:
                        on_transcript(data)

                    # Sinaliza que recebeu pelo menos UM resultado final
                    if is_final:
                        final_received.set()

                # Erro
                elif data.get("type") == "Error":
                    error_msg = data.get("error", data.get("message", "Unknown error"))
                    logger.error(f"[TalkLabs STT] ❌ Erro do servidor: {error_msg}")
                    final_received.set()

                # Tipo desconhecido
                else:
                    logger.warning(
                        f"[TalkLabs STT] ⚠️ Tipo de mensagem desconhecido: "
                        f"{data.get('type')} - Data: {data}"
                    )

        except asyncio.CancelledError:
            pass  # Normal quando task é cancelada
        except Exception as e:
            if "disconnect" not in str(e).lower() and "closed" not in str(e).lower():
                logger.error(f"[TalkLabs STT] ❌ Erro ao receber: {e}")
            final_received.set()

    async def close(self):
        """
        Fecha a conexão WebSocket persistente.

        Chame este método quando terminar de usar stream().
        """
        if self._ws:
            logger.info("[TalkLabs STT] 🔌 Fechando conexão WebSocket...")
            try:
                await self._ws.close()
            except Exception as e:
                logger.warning(f"[TalkLabs STT] ⚠️  Erro ao fechar: {e}")
            finally:
                self._ws = None
                self._ws_params = None
            logger.info("[TalkLabs STT] ✅ Conexão fechada")
