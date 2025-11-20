import logging

from narration._handler.common.record.utils import has_remote_record_marker, unmark_remote_record


class ForwardHandler(logging.Handler):
    def __init__(self, level: int = logging.DEBUG, logger: logging.Logger = None) -> None:
        super().__init__(level=level)
        self._logger = logger
        self._closed = False

    def handle(self, record: logging.LogRecord) -> None:
        if self._closed or self._logger is None or record is None:
            return

        # Logger.handle(...) calling this function must be ignored by this
        # forwarder to avoid self reflexive call loop
        if not has_remote_record_marker(record=record, state=True):
            return

        # Forward record to other handlers (except the current one) of this logger
        unmark_remote_record(record=record)
        self._logger.handle(record=record)

    def close(self) -> None:
        self._closed = True

    def emit(self, record):
        pass
