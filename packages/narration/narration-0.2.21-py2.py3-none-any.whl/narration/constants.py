from enum import Enum


class Backend(Enum):
    NATIVE = "native"  # Deprecated
    ZMQ = "zero-mq"
    DEFAULT = ZMQ
