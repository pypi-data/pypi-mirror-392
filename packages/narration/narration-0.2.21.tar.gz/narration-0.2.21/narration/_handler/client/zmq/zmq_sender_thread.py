import threading
from queue import Queue

from narration._handler.client.common.thread.base_sender_thread import BaseSenderThread
from narration._handler.common.zmq.zmq_socket import ZMQSocket
from narration._handler.common.socket.base_socket import BaseSocket
from narration._handler.common.zmq.zmq_resilient_socket import ZMQResilientSocket


class ZMQSenderThread(BaseSenderThread):
    def __init__(
        self,
        *args,
        name: str = None,
        sender_ready: threading.Event = None,
        socket_type: object = None,
        address: str = None,
        queue: Queue = None,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            name=name,
            sender_ready=sender_ready,
            daemon=True,
            write_timeout=2.0,
            queue=queue,
            **kwargs,
        )

        self._socket_type = socket_type
        self._address = address

    async def _create_socket(self) -> BaseSocket:
        zmq_socket = ZMQResilientSocket(self._socket_type, self._address, check=self._not_running)
        return ZMQSocket(zmq_socket=zmq_socket)
