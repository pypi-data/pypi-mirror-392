import logging
import threading

import zmq

from narration._misc.constants import DispatchMode
from narration._handler.common.util.utils import wait_for_event
from narration._handler.server.common.handler.base_server_handler import BaseServerHandler
from narration._handler.server.common.thread.base_receiver_thread import BaseReceiverThread
from narration._handler.server.zmq.zmq_receiver_thread import ZMQReceiverThread


class ZMQServerHandler(BaseServerHandler):
    def __init__(
        self,
        uuid: str = None,
        name: str = None,
        target_handler: logging.Handler = None,
        address: str = "tcp://127.0.0.1",
        level: int = logging.DEBUG,
        on_close_timeout: float = 1.0,
        message_dispatching: DispatchMode = DispatchMode.SYNC,
    ) -> None:
        super().__init__(
            uuid=uuid,
            name=name,
            target_handler=target_handler,
            level=level,
            on_close_timeout=on_close_timeout,
            message_dispatching=message_dispatching,
            group_id=None,
        )

        self._socket_type = zmq.PULL
        self._address = address
        self._socket = None

        dispatching_ready, self._group_id = self._assign_dispatch(
            group_id=self._address,
            record_emitter=self._record_emitter,
        )
        wait_for_event(dispatching_ready, 60, self._dispatch.thread.is_alive)

        self._address = self._dispatch.thread.address

    def _create_dispatch_thread(
        self, thread_name: str = None, dispatching_ready: threading.Event = None
    ) -> BaseReceiverThread:
        return ZMQReceiverThread(
            name=thread_name,
            receiver_ready=dispatching_ready,
            socket_type=self._socket_type,
            address=self._address,
        )
