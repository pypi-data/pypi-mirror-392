import threading
from asyncio.exceptions import CancelledError

from narration._handler.common.record.utils import mark_remote_record
from narration._misc.constants import NARRATION_DEBUG_HANDLER_THREAD_PREFIX
from narration._handler.common.payload.serialization.record_payload import (
    to_record_payload,
    to_unbinary_payload,
)
from narration._handler.common.payload.payload import PayloadType
from narration._handler.common.thread.base_op_thread import BaseOpThread
from narration._handler.common.misc.op_type import OpType
from narration._handler.common.socket.base_socket import BaseSocket
from narration._handler.common.socket.exception.readtimeoutexception import ReadTimeoutException
from narration._handler.common.callable import RecordSignal
from narration._debug.myself import get_debug_logger

_log = get_debug_logger(NARRATION_DEBUG_HANDLER_THREAD_PREFIX)


class BaseReceiverThread(BaseOpThread):
    def __init__(
        self,
        *args,
        name: str = None,
        receiver_ready: threading.Event = None,
        handler_id_to_record_emitters: dict[str, RecordSignal] = None,
        daemon: bool = False,
        read_timeout: float = 1.0,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            name=name,
            op_startup_completed=receiver_ready,
            daemon=daemon,
            op_timeout=read_timeout,
            op_type=OpType.RECEIVE,
            **kwargs,
        )
        self._handler_id_to_record_emitters = (
            handler_id_to_record_emitters if handler_id_to_record_emitters is not None else {}
        )

    def add_handler_id_to_record_emitter(
        self, handler_id: str = None, record_emitter: RecordSignal = None
    ) -> None:
        emitter = self._handler_id_to_record_emitters.get(handler_id, None)
        if emitter is None:
            self._handler_id_to_record_emitters[handler_id] = record_emitter

    def remove_handler_id_to_record_emitter(self, handler_id: str = None):
        self._handler_id_to_record_emitters.pop(handler_id, None)

    async def _create_socket(self) -> BaseSocket:
        raise NotImplementedError()

    async def _operate(self, socket: BaseSocket = None, op_timeout=None) -> bool:
        def has_read_record(record):
            return record is not None

        record_read = False
        try:
            payloads = await self._read_payload_from_socket(socket=socket, op_timeout=op_timeout)
            for payload in payloads:
                record = payload.record
                handler_id = payload.handler_id
                record_emitter = self._handler_id_to_record_emitters.get(handler_id, None)

                _log.debug(
                    "Record received with handler id %s %s: %s",
                    handler_id,
                    (
                        "discarded"
                        if record_emitter is None
                        else f"to be dispatched to {record_emitter}"
                    ),
                    record,
                )

                if record is None:
                    record_read = record_read or has_read_record(record)
                    continue
                if handler_id is None:
                    record_read = record_read or has_read_record(record)
                    continue
                if record_emitter is None:
                    record_read = record_read or has_read_record(record)
                    continue

                mark_remote_record(record=record, state=True)
                record_emitter.send(record)
                record_read = record_read or has_read_record(record)
        except ReadTimeoutException:
            _log.critical("Receiving message timeout", exc_info=1)
            return record_read or has_read_record(None)
        except BaseException as e:
            # Stop thread
            ignore_exception = isinstance(e, CancelledError)
            if not ignore_exception:
                _log.critical("Receiving message failed", exc_info=1)
                raise

        return record_read

    async def _read_payload_from_socket(
        self, socket: BaseSocket = None, op_timeout=None
    ) -> list[PayloadType]:
        binary_payload = await socket.read_payload(op_timeout=op_timeout)
        transport_payload = to_unbinary_payload(binary_payload)
        payloads = to_record_payload(transport_payload=transport_payload)
        for payload in payloads:
            _log.debug(
                "New record received from %s. Record: %s", payload.handler_id, payload.record
            )
        return payloads
