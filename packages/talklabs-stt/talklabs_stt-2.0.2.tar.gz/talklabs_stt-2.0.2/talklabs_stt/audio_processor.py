"""
TalkLabs STT SDK - Audio Processing

Audio preparation and conversion utilities.

Author: Francisco Lima
License: MIT
"""

import logging
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)


def load_audio(audio_path: str) -> tuple[np.ndarray, int]:
    """
    Carrega arquivo de áudio como int16.

    Args:
        audio_path: Caminho do arquivo de áudio

    Returns:
        tuple: (audio_data, sample_rate)

    Raises:
        Exception: Se houver erro ao ler o arquivo
    """
    try:
        audio_data, sample_rate = sf.read(audio_path, dtype='int16')
        return audio_data, sample_rate
    except Exception as e:
        logger.error(f"[TalkLabs STT] ❌ Erro ao carregar áudio: {e}")
        raise


def ensure_mono(audio_data: np.ndarray) -> np.ndarray:
    """
    Converte áudio para mono se necessário.

    Args:
        audio_data: Array de áudio (pode ser stereo ou mono)

    Returns:
        np.ndarray: Áudio em mono (int16)
    """
    if len(audio_data.shape) > 1:
        logger.debug("[TalkLabs STT] Convertendo stereo para mono")
        return audio_data.mean(axis=1).astype('int16')
    return audio_data


def to_pcm_bytes(audio_data: np.ndarray) -> bytes:
    """
    Converte array numpy para bytes PCM.

    Args:
        audio_data: Array de áudio int16

    Returns:
        bytes: Dados em formato PCM puro
    """
    return audio_data.tobytes()


def prepare_audio_for_streaming(audio_path: str, target_sample_rate: int) -> tuple[bytes, int]:
    """
    Prepara áudio para streaming WebSocket - OTIMIZADO.

    IMPORTANTE: Servidor já faz resample e normalização!

    Esta função apenas:
    1. Lê o arquivo
    2. Converte para mono se necessário
    3. Mantém como int16 (sem normalização prejudicial)
    4. Retorna bytes PCM puro + sample rate original

    O servidor receberá sample_rate via query params e fará resample se necessário.

    Args:
        audio_path: Caminho do arquivo de áudio
        target_sample_rate: Sample rate desejado (informativo, não usado)

    Returns:
        tuple: (audio_bytes, actual_sample_rate)

    Raises:
        Exception: Se houver erro no processamento
    """
    try:
        # 1. Carrega áudio
        audio_data, sample_rate = load_audio(audio_path)

        # 2. Garante mono
        audio_data = ensure_mono(audio_data)

        # 3. Converte para bytes
        audio_bytes = to_pcm_bytes(audio_data)

        # Retorna bytes puros + sample rate original
        # Servidor fará resample se sample_rate != 16000
        return audio_bytes, sample_rate

    except Exception as e:
        logger.error(f"[TalkLabs STT] ❌ Erro ao preparar áudio: {e}")
        raise
