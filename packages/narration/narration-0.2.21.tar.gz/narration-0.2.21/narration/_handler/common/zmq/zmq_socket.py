import errno

import zmq

from narration._debug.myself import get_debug_logger
from narration._handler.common.socket.base_socket import BaseSocket
from narration._handler.common.socket.exception.bindfailedexception import BindFailedException
from narration._handler.common.socket.exception.readtimeoutexception import ReadTimeoutException
from narration._handler.common.socket.exception.writetimeoutexception import WriteTimeoutException
from narration._handler.common.zmq.zmq_resilient_socket import ZMQResilientSocket
from narration._misc.constants import NARRATION_DEBUG_HANDLER_SOCKET_ZMQ_PREFIX

_log = get_debug_logger(NARRATION_DEBUG_HANDLER_SOCKET_ZMQ_PREFIX)


class ZMQSocket(BaseSocket):
    def __init__(self, zmq_socket: ZMQResilientSocket = None):
        super().__init__()
        self._zmq_socket = zmq_socket

    async def bind(self):
        try:
            self._zmq_socket.bind()
        except zmq.ZMQBindError as error:
            raise BindFailedException() from error

    async def connect(self):
        self._zmq_socket.connect()

    async def read_payload(self, op_timeout=None) -> bytes:
        try:
            return await self._zmq_socket.recv_bytes(timeout=op_timeout)
        except zmq.ZMQError as error:
            if error.errno == errno.EAGAIN:
                raise ReadTimeoutException() from error
            raise error

    async def write_payload(self, value: bytes, op_timeout=None):
        try:
            future = self._zmq_socket.send_bytes(value, timeout=op_timeout)
            return await future
        except zmq.ZMQError as error:
            if error.errno == errno.EAGAIN:
                raise WriteTimeoutException() from error
            raise error

    async def close(self):
        self._zmq_socket.close()

    @property
    def address(self) -> str:
        return self._zmq_socket.address
