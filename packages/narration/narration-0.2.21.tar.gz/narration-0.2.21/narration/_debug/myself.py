import logging

from narration.debug import get_debug_logger as _logger


def get_debug_logger(
    nane: str = None,
    env_name: str = "NARRATION_DEBUG",
    env_value_default: str = "0",
    env_value_enabled: str = "1",
    level=logging.DEBUG,
) -> logging.Logger:
    return _logger(
        name=nane,
        env_name=env_name,
        env_value_default=env_value_default,
        env_value_enabled=env_value_enabled,
        level=level,
    )
