from queue import Empty, Full

from narration._handler.common.socket.base_socket import BaseSocket
from narration._handler.common.socket.exception.readtimeoutexception import ReadTimeoutException
from narration._handler.common.socket.exception.writetimeoutexception import WriteTimeoutException


class NativeSocket(BaseSocket):
    def __init__(self, native_queue=None):
        super().__init__()
        self._native_queue = native_queue

    async def bind(self):
        pass

    async def connect(self):
        pass

    async def read_payload(self, op_timeout=None):
        try:
            return self._native_queue.get(block=True, timeout=op_timeout)
        except Empty as e:
            raise ReadTimeoutException() from e
        except BaseException as e1:
            raise e1

    async def write_payload(self, value, op_timeout=None):
        try:
            self._native_queue.put(value, block=True, timeout=op_timeout)
        except Full as e:
            raise WriteTimeoutException() from e
        except BaseException as e1:
            raise e1

    async def close(self):
        pass

    @property
    def address(self) -> str:
        return "no_address"
