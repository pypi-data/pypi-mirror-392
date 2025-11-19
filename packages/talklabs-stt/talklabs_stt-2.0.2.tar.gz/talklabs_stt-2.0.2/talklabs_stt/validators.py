"""
TalkLabs STT SDK - Input Validators

Centralized validation functions to eliminate code duplication.

Author: Francisco Lima
License: MIT
"""

import os


def validate_file_exists(path: str) -> None:
    """
    Valida se o arquivo existe.

    Args:
        path: Caminho do arquivo

    Raises:
        FileNotFoundError: Se o arquivo não existir
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")


def validate_api_key(api_key: str) -> None:
    """
    Valida se a API key foi fornecida.

    Args:
        api_key: Chave de API

    Raises:
        ValueError: Se a API key estiver vazia
    """
    if not api_key:
        raise ValueError("API key é obrigatória")
