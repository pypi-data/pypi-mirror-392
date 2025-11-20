import logging
from logging import makeLogRecord, NullHandler

null_handler = NullHandler()


def _record_to_dict(record, handler=null_handler):
    # this function is the core of python's logging._handler.SocketHandler
    # method ``makePickle``

    exception_info = record.exc_info
    if exception_info:
        # just to get traceback text into record.exc_text ...
        handler.format(record)
    # See issue #14436: If msg or args are objects, they may not be
    # available on the receiving end. So we convert the msg % args
    # to a string, save it as msg and zap the args.
    data = dict(record.__dict__)
    data["msg"] = record.getMessage()
    data["args"] = None
    data["exc_info"] = None
    # Issue #25685: delete 'message' if present: redundant with 'msg'
    data.pop("message", None)
    return data


def to_log_record_native_type(record: logging.LogRecord = None) -> dict:
    return _record_to_dict(record, handler=null_handler)


def from_log_record_native_type(data: dict) -> logging.LogRecord:
    return makeLogRecord(data)
