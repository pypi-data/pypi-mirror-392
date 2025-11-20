import logging

from narration._misc.constants import NARRATION_RECORD_PREFIX

ATTRIB_MARKER = f"_{NARRATION_RECORD_PREFIX}-marker"


def has_remote_record_marker(record: logging.LogRecord = None, state: bool = False) -> bool:
    return record is not None and getattr(record, ATTRIB_MARKER, None) == state


def mark_remote_record(record: logging.LogRecord = None, state: bool = False):
    if record is not None:
        setattr(record, ATTRIB_MARKER, state)


def unmark_remote_record(record: logging.LogRecord = None):
    if record is not None:
        delattr(record, ATTRIB_MARKER)
