import threading

from narration._handler.common.native.native_socket import NativeSocket
from narration._handler.server.common.thread.base_receiver_thread import BaseReceiverThread
from narration._handler.common.socket.base_socket import BaseSocket


class NativeReceiverThread(BaseReceiverThread):
    def __init__(
        self,
        *args,
        name: str = None,
        receiver_ready: threading.Event = None,
        handler=None,
        native_queue=None,
        **kwargs,
    ):
        super().__init__(
            *args, name=name, receiver_ready=receiver_ready, daemon=True, read_timeout=2.0, **kwargs
        )

        self._native_queue = native_queue

    async def _create_socket(self) -> BaseSocket:
        return NativeSocket(native_queue=self._native_queue)
