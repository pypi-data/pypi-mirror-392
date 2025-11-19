"""
TalkLabs STT SDK - Data Models

Contains dataclasses and models used across the SDK.

Author: Francisco Lima
License: MIT
"""

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class TranscriptionOptions:
    """
    Opções de transcrição para TalkLabs STT.

    Attributes:
        language: Código do idioma ISO 639-1 ("pt", "en", "es", etc.)
        detect_language: Detectar idioma automaticamente (ignora 'language')
        vad_filter: Voice Activity Detection - remove silêncios
        interim_results: Enviar resultados intermediários (WebSocket apenas)
        encoding: Formato de áudio (WebSocket apenas)
        sample_rate: Taxa de amostragem em Hz (WebSocket apenas)
        channels: Número de canais de áudio (WebSocket apenas)

    Note:
        O SDK usa exclusivamente o modelo "turbo" internamente.
        Pontuação e formatação inteligente são sempre aplicadas.

    Example:
        >>> opts = TranscriptionOptions(language="pt")
    """

    # Core parameters
    language: str = "pt"

    # Text processing
    detect_language: bool = False
    vad_filter: bool = False

    # WebSocket streaming parameters
    interim_results: bool = True
    encoding: str = "linear16"
    sample_rate: int = 16000
    channels: int = 1

    def to_query_params(self) -> Dict[str, str]:
        """
        Converte opções para query parameters HTTP.

        Returns:
            dict: Query parameters com valores convertidos para string

        Note:
            Model é sempre 'turbo' e punctuate/smart_format são sempre True.

        Example:
            >>> opts = TranscriptionOptions(language="pt")
            >>> params = opts.to_query_params()
            >>> # {'model': 'turbo', 'language': 'pt', ...}
        """
        params = {"model": "turbo", "punctuate": "true", "smart_format": "true"}
        for key, value in asdict(self).items():
            if isinstance(value, bool):
                params[key] = str(value).lower()
            elif value is not None:
                params[key] = str(value)
        return params

    def to_ws_params(self) -> Dict[str, str]:
        """
        Converte opções para query parameters WebSocket.

        Returns:
            dict: Query parameters específicos para WebSocket

        Note:
            Model é sempre 'turbo' e punctuate/smart_format são sempre True.
        """
        return {
            "model": "turbo",
            "language": self.language,
            "punctuate": "true",
            "smart_format": "true",
            "detect_language": str(self.detect_language).lower(),
            "vad_filter": str(self.vad_filter).lower(),
            "encoding": self.encoding,
            "sample_rate": str(self.sample_rate),
            "channels": str(self.channels),
            "interim_results": str(self.interim_results).lower()
        }
