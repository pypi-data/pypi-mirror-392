import logging
import os
import sys
import loguru

import attrs


@attrs.define
class _NarrationLoggerState:
    loggers_configured: dict = {}
    loggers_enabled: dict = {}
    loggers: dict = {}


_narration_logger_state = _NarrationLoggerState()


class DebugLogger(logging.Logger):
    def __init__(self, name, level):
        super().__init__(name, level)

    def isEnabledFor(self, level: int) -> bool:
        # Do not use logging._acquireLock.
        # Reason: baseHandler's close() tries to shutdown the BaseHandler's receive/sender thread. The thread sometimes
        # log records, which internally would call logging._acquireLock. Thereby creating a deadlock when 2 different
        # threads try to acquire the lock
        return level >= self.getEffectiveLevel()


class LoguruHandler(logging.Handler):
    def __init__(self, logger, level):
        super().__init__(level)
        self._logger = logger
        self.severity_to_methods = {
            logging.NOTSET: logger.debug,
            logging.DEBUG: logger.debug,
            logging.INFO: logger.info,
            logging.WARN: logger.warning,
            logging.WARNING: logger.warning,
            logging.ERROR: logger.error,
            logging.CRITICAL: logger.critical,
        }

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.severity_to_methods[record.levelno](msg)
        except Exception:
            self.handleError(record)


def get_debug_logger(
    name: str = None,
    env_name: str = "DEBUG",
    env_value_default: str = "0",
    env_value_enabled: str = "1",
    level=logging.DEBUG,
):
    enabled = os.environ.get(env_name, env_value_default) == env_value_enabled
    return _get_debug_logger(name=name, enabled_override=enabled, level=level)


def is_debug_logger_enabled(name: str = None):
    return _narration_logger_state.loggers_enabled.get(name, False)


def configure_debug_loggers(names: list[str] = None, enabled: bool = None, level=logging.DEBUG):
    if names is None:
        names = []
    for name in names:
        _configure_debug_logger_once(name=name, enabled=enabled, level=level)


def _get_logger(name: str = None):
    logger = _narration_logger_state.loggers.get(name, None)
    if logger is None:
        _logger = loguru.logger
        logger = DebugLogger(name=name, level=logging.NOTSET)
        _narration_logger_state.loggers[name] = logger
    return logger


def _get_debug_logger(name: str = None, enabled_override: bool = None, level: int = logging.DEBUG):
    configure_debug_loggers(names=[name], enabled=enabled_override, level=level)
    return _get_logger(name=name)


def _configure_debug_logger_once(name: str = None, enabled: bool = None, level=logging.DEBUG):
    logger = _get_logger(name=name)

    # Do not reconfigure if enabled has not changed
    if _narration_logger_state.loggers_configured.get(name, None) is not None:
        if enabled is None:
            return
        if not enabled == logger.disabled:
            return

    logger.disabled = not enabled
    logger.setLevel(level if enabled else logging.CRITICAL)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(name)s:PID%(process)d:T%(thread)d:%(levelname)s:%(message)s"
        )

        count = len(list(_narration_logger_state.loggers.keys()))
        if count == 1:
            loguru.logger.remove()
            loguru.logger.add(
                sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss.SSSSSS}:{message}", level="DEBUG"
            )

        handler = LoguruHandler(loguru.logger, level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info("%s _debug logger activated", name)

    _narration_logger_state.loggers_configured[name] = True
    _narration_logger_state.loggers_enabled[name] = enabled
