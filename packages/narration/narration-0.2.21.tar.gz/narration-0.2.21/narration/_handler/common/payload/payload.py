import logging
from typing import Union

import msgspec


class LogRecordPayload(msgspec.Struct):
    record: logging.LogRecord = None
    handler_id: str = None


PayloadType = Union[LogRecordPayload]
