from narration._handler.common.socket.exception.bindfailedexception import BindFailedException
from narration._handler.common.socket.exception.connectfailedexception import ConnectFailedException
from narration._handler.common.socket.exception.readtimeoutexception import ReadTimeoutException
from narration._handler.common.socket.exception.writetimeoutexception import WriteTimeoutException


class BaseSocket:
    def __init__(
        self,
    ):
        pass

    async def bind(self):
        raise BindFailedException()

    async def connect(self):
        raise ConnectFailedException()

    async def read_payload(self, op_timeout=None) -> bytes:
        raise ReadTimeoutException()

    async def write_payload(self, value: bytes, op_timeout=None):
        raise WriteTimeoutException()

    async def close(self):
        raise NotImplementedError()

    @property
    def address(self) -> str:
        raise NotImplementedError()
