"""
TalkLabs STT SDK - Main Client

Thin orchestrator client that delegates to specialized components.

Author: Francisco Lima
License: MIT
"""

import logging
import requests
from typing import Optional, Callable

from .models import TranscriptionOptions
from .validators import validate_api_key
from .http_client import HTTPTranscriber
from .websocket_stream import WebSocketStreamer

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class STTClient:
    """
    Cliente TalkLabs STT para transcrição de áudio.

    Features:
        - REST API para transcrição completa de arquivos
        - WebSocket para streaming em tempo real
        - Modelo de transcrição otimizado (turbo)
        - Processamento de texto inteligente (pontuação, formatação)
        - Voice Activity Detection (VAD)
        - API compatível com Deepgram

    Args:
        api_key: Chave de API TalkLabs (ex: "tlk_live_xxxxx")
        timeout: Timeout para requisições em segundos (default: 300)

    Attributes:
        api_key: Chave de API fornecida
        base_url: URL base da API (fixo: "https://api.talklabs.com.br/api/stt")
        timeout: Timeout configurado em segundos

    Example:
        >>> from talklabs_stt import STTClient
        >>>
        >>> # Inicialização básica
        >>> client = STTClient(api_key="tlk_live_xxxxx")
        >>>
        >>> # Com timeout customizado
        >>> client = STTClient(api_key="tlk_live_xxxxx", timeout=600)
        >>>
        >>> # REST API - transcrição completa
        >>> result = client.transcribe_file("audio.wav")
        >>> print(result["results"]["channels"][0]["alternatives"][0]["transcript"])
        >>>
        >>> # WebSocket Streaming - tempo real
        >>> async def main():
        ...     def on_transcript(data):
        ...         if data["is_final"]:
        ...             print(f"Final: {data['channel']['alternatives'][0]['transcript']}")
        ...
        ...     await client.transcribe_stream(
        ...         "audio.wav",
        ...         on_transcript=on_transcript
        ...     )
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        timeout: int = 300
    ):
        """
        Inicializa o cliente STT.

        Args:
            api_key: API key do TalkLabs
            timeout: Timeout em segundos

        Raises:
            ValueError: Se api_key não for fornecida
        """
        validate_api_key(api_key)

        self.api_key = api_key
        self.base_url = "https://api.talklabs.com.br/api/stt"
        self.timeout = timeout

        # Componentes especializados
        self._http = HTTPTranscriber(api_key, self.base_url, timeout)
        self._ws = WebSocketStreamer(api_key, self.base_url)

        logger.info(f"[TalkLabs STT] 🎤 Cliente inicializado: {self.base_url}")

    # ============================================================
    # CONTEXT MANAGER SUPPORT (async with)
    # ============================================================

    async def __aenter__(self):
        """Suporte para 'async with' - retorna o cliente"""
        return self

    async def __aexit__(self, *_):
        """Suporte para 'async with' - fecha conexão automaticamente"""
        await self.close()
        return False

    # ============================================================
    # REST API METHODS
    # ============================================================

    def transcribe_file(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions] = None,
        **kwargs
    ) -> dict:
        """
        Transcreve um arquivo de áudio completo via REST API (síncrono).

        Args:
            audio_path: Caminho para o arquivo de áudio
            options: Opções de transcrição (ou None para padrões)
            **kwargs: Parâmetros adicionais (language, punctuate, etc.)
                     Nota: O parâmetro 'model' é ignorado - sempre usa 'turbo'

        Returns:
            dict: Resultado da transcrição no formato Deepgram-compatible:
                {
                    "metadata": {...},
                    "results": {
                        "channels": [{
                            "alternatives": [{
                                "transcript": "texto transcrito",
                                "confidence": 0.95,
                                "words": [...]
                            }]
                        }]
                    }
                }

        Example:
            >>> # Uso básico
            >>> result = client.transcribe_file("audio.wav")
            >>>
            >>> # Com opções
            >>> opts = TranscriptionOptions(language="en", punctuate=True)
            >>> result = client.transcribe_file("audio.wav", options=opts)
            >>>
            >>> # Com kwargs diretos
            >>> result = client.transcribe_file(
            ...     "audio.wav",
            ...     language="pt",
            ...     punctuate=True,
            ...     smart_format=True
            ... )

        Raises:
            FileNotFoundError: Se o arquivo de áudio não existir
            requests.HTTPError: Se a API retornar erro
            Exception: Outros erros de rede ou processamento
        """
        return self._http.transcribe(audio_path, options, **kwargs)

    # ============================================================
    # WEBSOCKET STREAMING METHODS
    # ============================================================

    async def transcribe_stream(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions] = None,
        on_transcript: Optional[Callable[[dict], None]] = None,
        on_metadata: Optional[Callable[[dict], None]] = None,
        chunk_size: int = 800000,  # 25s @ 16kHz
        **kwargs
    ):
        """
        Transcreve áudio via WebSocket com CONEXÃO PERSISTENTE.

        WebSocket mantém conexão aberta automaticamente:
        - Primeira chamada: Abre conexão
        - Chamadas seguintes: Reutiliza automaticamente
        - Para fechar: Chame close() quando terminar

        Args:
            audio_path: Caminho para o arquivo de áudio
            options: Opções (usadas apenas na primeira chamada para abrir conexão)
            on_transcript: Callback para cada transcrição recebida
            on_metadata: Callback para metadata da sessão
            chunk_size: Tamanho dos chunks em bytes (default: 800000 = 25s @ 16kHz)
            **kwargs: Parâmetros adicionais (language, punctuate, etc.)
                     Nota: O parâmetro 'model' é ignorado - sempre usa 'turbo'

        Example:
            >>> async def main():
            ...     client = STTClient(api_key=API_KEY)
            ...
            ...     def on_transcript(data):
            ...         if data["is_final"]:
            ...             print(f"Final: {data['channel']['alternatives'][0]['transcript']}")
            ...
            ...     # Primeira chamada - abre conexão
            ...     await client.transcribe_stream(
            ...         "audio1.wav", language="pt",
            ...         on_transcript=on_transcript
            ...     )
            ...
            ...     # Segunda chamada - reutiliza conexão automaticamente
            ...     await client.transcribe_stream("audio2.wav", on_transcript=on_transcript)
            ...
            ...     # Fecha quando terminar
            ...     await client.close()
            >>>
            >>> asyncio.run(main())

        Raises:
            FileNotFoundError: Se o arquivo não existir
            websockets.exceptions.WebSocketException: Erro de conexão
        """
        await self._ws.stream(
            audio_path,
            options,
            on_transcript,
            on_metadata,
            chunk_size,
            **kwargs
        )

    async def close(self):
        """
        Fecha a conexão WebSocket persistente.

        Chame este método quando terminar de usar transcribe_stream().

        Example:
            >>> await client.transcribe_stream("audio1.wav", ...)
            >>> await client.transcribe_stream("audio2.wav", ...)
            >>> await client.close()  # Fecha a conexão
        """
        await self._ws.close()

    # ============================================================
    # UTILITY METHODS
    # ============================================================

    def list_models(self) -> dict:
        """
        Lista os modelos de transcrição disponíveis no servidor.

        Nota:
            Este método é mantido para fins informativos e debugging.
            O SDK usa exclusivamente o modelo "turbo" independente dos
            modelos disponíveis no servidor.

        Returns:
            dict: Lista de modelos disponíveis no servidor

        Example:
            >>> models = client.list_models()
            >>> for model in models["models"]:
            ...     print(model["name"])

        Raises:
            requests.HTTPError: Se a API retornar erro
        """
        url = f"{self.base_url}/v1/models"
        headers = {"xi-api-key": self.api_key}

        logger.info(f"[TalkLabs STT] 📋 Listando modelos: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            model_count = len(result.get("models", []))
            logger.info(f"[TalkLabs STT] ✅ {model_count} modelo(s) disponível(is)")
            return result

        except Exception as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro ao listar modelos: {e}")
            raise
