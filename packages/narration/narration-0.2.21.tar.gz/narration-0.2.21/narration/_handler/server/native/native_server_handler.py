import threading

from narration._misc.constants import DispatchMode
from narration._handler.common.util.utils import wait_for_event
from narration._handler.server.common.thread.base_receiver_thread import BaseReceiverThread
from narration._handler.server.common.handler.base_server_handler import BaseServerHandler
from narration._handler.server.native.native_receiver_thread import NativeReceiverThread


class NativeServerHandler(BaseServerHandler):
    def __init__(
        self,
        uuid: str = None,
        name: str = None,
        target_handler=None,
        queue=None,
        level: int = None,
        on_close_timeout: float = 1.0,
        message_dispatching: DispatchMode = DispatchMode.SYNC,
    ):
        super().__init__(
            uuid=uuid,
            name=name,
            target_handler=target_handler,
            level=target_handler.level,
            on_close_timeout=on_close_timeout,
            message_dispatching=message_dispatching,
            group_id=None,
        )
        self._native_queue = queue

        group_id = "native_group_id"
        dispatching_ready, self._group_id = self._assign_dispatch(
            group_id=group_id,
            record_emitter=self._record_emitter,
        )
        wait_for_event(dispatching_ready, 60, self._dispatch.thread.is_alive)

    def _create_dispatch_thread(
        self, thread_name: str = None, dispatching_ready: threading.Event = None
    ) -> BaseReceiverThread:
        return NativeReceiverThread(
            name=thread_name, receiver_ready=dispatching_ready, native_queue=self._native_queue
        )
