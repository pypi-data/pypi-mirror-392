import logging

from narration._debug.logger import get_debug_logger as _get_debug_logger
from narration._debug.logger import is_debug_logger_enabled as _is_debug_logger_enabled


def get_debug_logger(
    name: str = None,
    env_name: str = "DEBUG",
    env_value_default: str = "0",
    env_value_enabled: str = "1",
    level=logging.DEBUG,
) -> logging.Logger:
    """To enable debugging you library set the environment variable ``env_name=1``"""
    return _get_debug_logger(
        name=name,
        env_name=env_name,
        env_value_default=env_value_default,
        env_value_enabled=env_value_enabled,
        level=level,
    )


def is_debug_logger_enabled(name: str = None) -> bool:
    return _is_debug_logger_enabled(name=name)
