"""
TalkLabs STT SDK - Decorators

Reusable decorators for error handling and logging.

Author: Francisco Lima
License: MIT
"""

import functools
import inspect
import logging
from typing import Callable


def handle_errors(logger: logging.Logger):
    """
    Decorator para tratamento consistente de erros.

    Captura exceções, loga e re-raise de forma padronizada.

    Args:
        logger: Logger instance para registrar erros

    Example:
        >>> @handle_errors(logger)
        ... async def send_data(...):
        ...     # código que pode falhar
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[TalkLabs STT] ❌ Erro em {func.__name__}: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[TalkLabs STT] ❌ Erro em {func.__name__}: {e}")
                raise

        # Detecta se é função async ou sync
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
