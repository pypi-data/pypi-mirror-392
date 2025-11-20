from __future__ import annotations

import threading
from asyncio.exceptions import CancelledError
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Empty, Queue
from typing import Any

from narration._broker.dispatch_status import DispatchStatus
from narration._misc.constants import NARRATION_DEBUG_HANDLER_THREAD_PREFIX
from narration._handler.common.payload.serialization.record_payload import (
    to_transport_payload,
    to_binary_payload,
)
from narration._handler.common.thread.base_op_thread import BaseOpThread
from narration._handler.common.misc.op_type import OpType
from narration._handler.common.socket.exception.optimeoutexception import OpTimeoutException
from narration._handler.common.socket.base_socket import BaseSocket
from narration._debug.myself import get_debug_logger

_log = get_debug_logger(NARRATION_DEBUG_HANDLER_THREAD_PREFIX)


class NoPayloadException(BaseException):
    pass


class BaseSenderThread(BaseOpThread):
    def __init__(
        self,
        *args,
        name: str = None,
        sender_ready: threading.Event = None,
        daemon: bool = False,
        write_timeout: float = 1.0,
        queue: Queue[DispatchStatus] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            name=name,
            op_startup_completed=sender_ready,
            daemon=daemon,
            op_timeout=write_timeout,
            op_type=OpType.SEND,
            **kwargs,
        )
        self._queue = queue
        self._pending_dispatch_statuses = []
        self._thread_pool = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix=f"blocking_io_{self.name}"
        )
        self._blocking_io_interrupted = threading.Event()

    @property
    def queue(self) -> Queue[DispatchStatus]:
        return self._queue

    async def get_from_queue(
        self, timeout: float = 0.025, interrupted: threading.Event = None
    ) -> list[Any]:
        def blocking_queue_read(timeout: float, interrupted_cond: threading.Event):
            if interrupted_cond.wait(timeout if timeout is not None else 0.1):
                raise InterruptedError("blocking io interrupted")

            items = []
            while True:
                try:
                    item = self.queue.get(block=False)
                    items.extend([item])
                except Empty:
                    # nothing left in the queue
                    return items

        return await self._loop.run_in_executor(
            self._thread_pool, blocking_queue_read, timeout, interrupted
        )

    async def _create_socket(self) -> BaseSocket:
        raise NotImplementedError()

    async def _operate(self, socket: BaseSocket = None, op_timeout=None) -> bool:
        def raise_exception(exeption):
            def dummy(*args):
                raise exeption

            return dummy

        def return_value(value):
            def dummy(*args):
                return value

            return dummy

        consumed = False
        record_written = False
        dispatch_statuses: list[DispatchStatus] = []
        try:
            # Try reading multiple dispatch and aggregate their record
            # messages over a single transport message
            has_new_dispatch_status = False
            retry_pending = len(self._pending_dispatch_statuses) > 0

            # Read N dispatch or reuse pending ones
            if retry_pending:
                dispatch_statuses.extend(self._pending_dispatch_statuses)
            else:
                dispatch_statuses2 = await self.get_from_queue(
                    timeout=op_timeout, interrupted=self._blocking_io_interrupted
                )
                has_new_dispatch_status = bool(dispatch_statuses2)
                dispatch_statuses.extend(dispatch_statuses2)

            if not has_new_dispatch_status:
                consumed = True
                record_written = False

                for dispatch_status in dispatch_statuses:
                    dispatch_status.emit(
                        emitter=raise_exception(NoPayloadException()),
                        drop_completion_if_successful=False,
                    )
            else:
                payloads = [d.payload for d in dispatch_statuses]
                transport_payload = to_transport_payload(payloads=payloads)
                _log.debug(
                    "Aggregating %d record payload per transport payload sent", len(payloads)
                )

                result = await self._write_payload_to_socket(
                    socket=socket,
                    transport_payload=transport_payload,
                    op_timeout=op_timeout,
                    retrying=retry_pending,
                )
                record_written = result is None
                consumed = record_written

                for dispatch_status in dispatch_statuses:
                    dispatch_status.emit(
                        emitter=return_value(record_written),
                        drop_completion_if_successful=False,
                    )

                self._pending_dispatch_statuses.clear()

            return record_written
        except OpTimeoutException:
            self._pending_dispatch_statuses = dispatch_statuses
            return record_written
        except BaseException as ex:
            # Stop thread
            if len(dispatch_statuses) > 0:
                consumed = True
                for dispatch_status in dispatch_statuses:
                    dispatch_status.emit(
                        emitter=raise_exception(ex), drop_completion_if_successful=False
                    )
            ignore_exception = isinstance(ex, CancelledError)
            if not ignore_exception:
                _log.critical("Sending message(s) failed", exc_info=1)
                raise
        finally:
            if consumed:
                for _ in dispatch_statuses:
                    self._queue.task_done()

    async def _write_payload_to_socket(
        self,
        socket: BaseSocket = None,
        transport_payload: object = None,
        op_timeout=0,
        retrying: bool = False,
    ):
        _log.debug(
            "%s record to send (%s) %s",
            "Retry" if retrying else "New",
            op_timeout + "s" if op_timeout is not None else "no timeout",
            transport_payload,
        )
        binary_payload = to_binary_payload(data=transport_payload)
        return await socket.write_payload(binary_payload, op_timeout=op_timeout)

    def shutdown(self, timeout: float = None):
        # Cancel all pending queue record status, otherwise wait till they complete
        try:
            while True:
                dispatch_status = self.queue.get_nowait()
                try:
                    future = dispatch_status.future
                    if future.done():
                        continue

                    _log.debug("Try cancelling dispatch status %s", dispatch_status.payload)
                    cancelled = future.cancel()
                    if not cancelled:
                        try:
                            future.result(timeout=None)
                        except BaseException:
                            _log.warning(
                                "%s raised exception.", dispatch_status.payload, exc_info=1
                            )
                finally:
                    self.queue.task_done()
        except Empty:
            # Queue cleared
            pass
        finally:
            # Queue is cleared by now. Join will return immediately (otherwise programmer error)
            self.queue.join()

        # Wait till shutdown thread reading from the queue stops
        super().shutdown(timeout=timeout)

        # Shutdown "blocking io" thread pool
        self._blocking_io_interrupted.set()
        self._thread_pool.shutdown(wait=True)
