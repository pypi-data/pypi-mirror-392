import logging
import threading
from queue import Queue

import blinker
import zmq

from narration._debug.myself import get_debug_logger
from narration._misc.constants import DispatchMode, NARRATION_DEBUG_HANDLER_ZMQ_PREFIX
from narration._handler.client.common.handler.base_client_handler import BaseClientHandler
from narration._handler.client.common.thread.base_sender_thread import BaseSenderThread
from narration._handler.client.zmq.zmq_sender_thread import ZMQSenderThread
from narration._handler.common.util.utils import wait_for_event

_log = get_debug_logger(NARRATION_DEBUG_HANDLER_ZMQ_PREFIX)


class ZMQClientHandler(BaseClientHandler):
    def __init__(
        self,
        uuid: str = None,
        name: str = None,
        address: str = None,
        level: int = logging.DEBUG,
        on_close_timeout: float = 1.0,
        message_dispatching: DispatchMode = DispatchMode.SYNC,
        group_id: str = None,
    ) -> None:
        super().__init__(
            uuid=uuid,
            name=name,
            record_emitter=blinker.Signal(),
            level=level,
            on_close_timeout=on_close_timeout,
            message_dispatching=message_dispatching,
            group_id=group_id,
        )

        self._socket_type = zmq.PUSH
        self._address = address

        self._group_id = self._address
        dispatch_ready, self._group_id = self._assign_dispatch(
            group_id=self._address,
            record_emitter=self._record_emitter,
        )
        wait_for_event(dispatch_ready, 60, self._dispatch.thread.is_alive)
        _log.debug("Client address: %s, group id %s", self._address, self._group_id)

    def _create_dispatch_thread(
        self, thread_name: str = None, dispatching_ready: threading.Event = None
    ) -> BaseSenderThread:
        return ZMQSenderThread(
            name=thread_name,
            sender_ready=dispatching_ready,
            socket_type=self._socket_type,
            address=self._address,
            queue=Queue(-1),
        )
