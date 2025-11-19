"""
TalkLabs STT SDK - HTTP Client

REST API transcription logic.

Author: Francisco Lima
License: MIT
"""

import logging
import requests
from typing import Optional
from .models import TranscriptionOptions
from .validators import validate_file_exists

logger = logging.getLogger(__name__)


class HTTPTranscriber:
    """
    Cliente HTTP para transcrição via REST API.

    Responsável por:
    - Enviar arquivos de áudio para API REST
    - Processar respostas
    - Logging de operações HTTP
    """

    def __init__(self, api_key: str, base_url: str, timeout: int = 300):
        """
        Inicializa o cliente HTTP.

        Args:
            api_key: Chave de API
            base_url: URL base da API
            timeout: Timeout em segundos
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    def transcribe(
        self,
        audio_path: str,
        options: Optional[TranscriptionOptions] = None,
        **kwargs
    ) -> dict:
        """
        Transcreve um arquivo de áudio completo via REST API.

        Args:
            audio_path: Caminho para o arquivo de áudio
            options: Opções de transcrição (ou None para padrões)
            **kwargs: Parâmetros adicionais (model, language, etc.)

        Returns:
            dict: Resultado da transcrição no formato Deepgram-compatible

        Raises:
            FileNotFoundError: Se o arquivo de áudio não existir
            requests.HTTPError: Se a API retornar erro
            Exception: Outros erros de rede ou processamento
        """
        # Valida arquivo
        validate_file_exists(audio_path)

        # Prepara opções
        if options is None:
            options = TranscriptionOptions()

        # Override com kwargs
        for key, value in kwargs.items():
            if hasattr(options, key):
                setattr(options, key, value)

        # Força modelo 'turbo' - outros valores são ignorados
        options.model = "turbo"

        # Lê arquivo de áudio
        logger.info(f"[TalkLabs STT] 📂 Lendo arquivo: {audio_path}")
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        # Monta URL e headers
        url = f"{self.base_url}/v1/listen"
        headers = {
            "Content-Type": "audio/wav",
            "xi-api-key": self.api_key
        }

        # Query parameters
        params = options.to_query_params()

        logger.info(f"[TalkLabs STT] 🔄 Enviando para API: {url}")
        logger.debug(f"[TalkLabs STT] Parâmetros: {params}")

        try:
            # Faz requisição
            response = requests.post(
                url,
                params=params,
                headers=headers,
                data=audio_data,
                timeout=self.timeout
            )

            # Valida resposta
            if response.status_code != 200:
                error_msg = f"Erro {response.status_code}: {response.text}"
                logger.error(f"[TalkLabs STT] ❌ {error_msg}")
                raise Exception(error_msg)

            # Parse JSON
            result = response.json()

            # Log sucesso
            channels = result.get("results", {}).get("channels", [{}])
            alternatives = channels[0].get("alternatives", [{}])
            transcript = alternatives[0].get("transcript", "")
            logger.info(
                f"[TalkLabs STT] ✅ Transcrição completa: "
                f"{len(transcript)} caracteres"
            )

            return result

        except requests.RequestException as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro na requisição: {e}")
            raise
        except Exception as e:
            logger.exception(f"[TalkLabs STT] ❌ Erro inesperado: {e}")
            raise
