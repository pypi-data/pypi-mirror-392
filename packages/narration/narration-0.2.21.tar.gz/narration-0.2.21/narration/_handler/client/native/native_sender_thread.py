import threading
from queue import Queue

from narration._handler.client.common.thread.base_sender_thread import BaseSenderThread
from narration._handler.common.native.native_socket import NativeSocket
from narration._handler.common.socket.base_socket import BaseSocket


class NativeSenderThread(BaseSenderThread):
    def __init__(
        self,
        *args,
        name: str = None,
        sender_ready: threading.Event = None,
        queue: Queue = None,
        native_queue: Queue = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            name=name,
            sender_ready=sender_ready,
            daemon=True,
            write_timeout=2.0,
            queue=queue,
            **kwargs,
        )
        self._native_queue = native_queue

    async def _create_socket(self) -> BaseSocket:
        return NativeSocket(native_queue=self._native_queue)
