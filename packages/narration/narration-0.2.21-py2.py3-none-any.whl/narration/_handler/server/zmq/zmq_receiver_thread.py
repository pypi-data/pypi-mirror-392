import threading

import zmq

from narration._handler.common.zmq.zmq_socket import ZMQSocket
from narration._handler.server.common.thread.base_receiver_thread import (
    BaseReceiverThread,
)
from narration._handler.common.socket.base_socket import BaseSocket
from narration._handler.common.zmq.zmq_resilient_socket import ZMQResilientSocket


class ZMQReceiverThread(BaseReceiverThread):
    def __init__(
        self,
        *args,
        name: str = None,
        receiver_ready: threading.Event = None,
        socket_type: zmq.SocketType = None,
        address: str = None,
        **kwargs,
    ) -> None:
        super().__init__(
            name=name, receiver_ready=receiver_ready, daemon=True, read_timeout=2.0, *args, **kwargs
        )

        self._socket_type = socket_type
        self._address = address

    async def _create_socket(self) -> BaseSocket:
        zmq_socket = ZMQResilientSocket(self._socket_type, self._address, check=self._not_running)
        return ZMQSocket(zmq_socket=zmq_socket)

    @property
    def address(self) -> str:
        return self._socket.address
