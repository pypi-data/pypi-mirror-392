import asyncio
from asyncio.events import AbstractEventLoop
from contextlib import suppress

from narration._debug.logger import is_debug_logger_enabled
from narration._handler.common.socket.base_socket import BaseSocket
from narration._handler.common.socket.exception.bindfailedexception import BindFailedException
import threading
import time

from narration._misc.constants import NARRATION_DEBUG_HANDLER_THREAD_PREFIX
from narration._handler.common.misc.op_type import OpType
from narration._debug.myself import get_debug_logger
from narration._handler.common.socket.exception.connectfailedexception import ConnectFailedException

_log = get_debug_logger(NARRATION_DEBUG_HANDLER_THREAD_PREFIX)


class BaseOpThread(threading.Thread):
    def __init__(
        self,
        *args,
        name: str = None,
        op_startup_completed: threading.Event = None,
        daemon: bool = False,
        op_timeout: float = 1.0,
        op_type: OpType = None,
        **kwargs,
    ) -> None:
        super().__init__(None, None, name, *args, **kwargs, daemon=daemon)

        self._op_type = op_type
        self._startup_completed = op_startup_completed
        self._max_op_timeout = op_timeout
        self._running = False
        self._shutdown_completed = threading.Event()
        self._shutdown_start_time = -1
        self._loop: AbstractEventLoop = None
        self._socket = None

    @property
    def startup_completed(self) -> threading.Event:
        return self._startup_completed

    @property
    def shutdown_completed(self) -> threading.Event:
        return self._shutdown_completed

    def _not_running(self):
        return not self._running

    async def _create_socket(self) -> BaseSocket:
        raise NotImplementedError()

    async def _bind_to_socket(self, socket: BaseSocket = None) -> bool:
        """
        Bind to socket
        :param socket:
        :param op_ready:
        :return:
        """
        try:
            await socket.bind()
            _log.debug("Socket bound for %sing", self._op_type.value)
            return True
        except BindFailedException:
            _log.warning("Socket binding failed for %sing", self._op_type.value, exc_info=1)
            return False

    async def _unbind_from_socket(self, socket: BaseSocket = None, bound: bool = False):
        """
        Unbind from socket
        :param socket:
        :param bound:
        :return:
        """
        try:
            if bound:
                await socket.close()
                _log.debug("Socket unbound for %sing", self._op_type.value)
        except BaseException:
            _log.error("Socket unbind failed for %sing", self._op_type.value, exc_info=1)

    async def _connect_to_socket(self, socket: BaseSocket = None) -> bool:
        try:
            await socket.connect()
            _log.debug("Socket connected for %sing", self._op_type.value)
            return True
        except ConnectFailedException:
            _log.error("Socket connection failed for %sing", self._op_type.value, exc_info=1)
            return False

    async def _disconnect_from_socket(self, socket: BaseSocket = None, connected: bool = None):
        try:
            if connected:
                await socket.close()
                _log.debug("Socket disconnected for %sing", self._op_type.value)
        except BaseException:
            _log.error("Socket disconnection failed for %sing", self._op_type.value, exc_info=1)

    async def _operate(self, socket: BaseSocket = None, op_timeout=None) -> bool:
        raise NotImplementedError()

    async def _runner(self):
        self._running = True
        self._log_thread_started()
        shutdown_duration = None
        try:
            operating = False
            dirty_shutdown = False

            # Create socket
            self._socket = socket = await self._create_socket()
            bound = False
            connected = False
            if self._op_type == OpType.RECEIVE:
                # Bind to socket
                bound = await self._bind_to_socket(socket=socket)
                # Thread running/ready only if socket is bound
                self._running = bound
                self._startup_completed.set()
            elif self._op_type == OpType.SEND:
                # Connect to socket
                connected = await self._connect_to_socket(socket=socket)
                # Thread running/ready only if socket is connected
                self._running = connected
                self._startup_completed.set()
            else:
                self._running = False

            # Case1: Thread is started => self._running == True
            # Case2: Thread is requested to stop. Thread will stop when:
            #        - no more ops are successful
            while self._running or operating:
                try:
                    _log.debug("%sing thread about to block on op", self._op_type.value)
                    operating = await self._operate(socket=socket, op_timeout=None)
                except asyncio.CancelledError:
                    _log.warning(
                        "%sing thread is interrupted by handler forceful shutdown",
                        self._op_type.value,
                        exc_info=1,
                    )
                    self._running = False
                    operating = False
                    dirty_shutdown = True
                except (KeyboardInterrupt, SystemExit):
                    # Stop thread
                    _log.warning(
                        "%sing thread is interrupted by user or system exit",
                        self._op_type.value,
                        exc_info=1,
                    )
                    self._running = False
                    operating = False
                    dirty_shutdown = True
                except BaseException:
                    # Stop thread
                    _log.warning(
                        "%sing thread is interrupted by unknown error",
                        self._op_type.value,
                        exc_info=1,
                    )
                    self._running = False
                    operating = False
                    dirty_shutdown = True
                finally:
                    if self._shutdown_start_time is None:
                        self._shutdown_start_time = time.perf_counter()

                self._log_thread_status(self._running, operating, dirty_shutdown, None)
        finally:
            shutdown_duration = time.perf_counter() - self._shutdown_start_time

            self._log_thread_status(self._running, operating, dirty_shutdown, shutdown_duration)

            # Destroy socket
            try:
                if self._op_type == OpType.RECEIVE:
                    await self._unbind_from_socket(socket=socket, bound=bound)
                elif self._op_type == OpType.SEND:
                    await self._disconnect_from_socket(socket=socket, connected=connected)
            finally:
                shutdown_duration = time.perf_counter() - self._shutdown_start_time
                self._log_thread_stopped(duration=shutdown_duration)
                self._shutdown_completed.set()

    def run(self):
        enabled = is_debug_logger_enabled(name=NARRATION_DEBUG_HANDLER_THREAD_PREFIX)
        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(enabled)
        asyncio.set_event_loop(self._loop)
        try:
            _future = asyncio.ensure_future(self._runner(), loop=self._loop)  # noqa: W0612
            # Run loop until explicitly stopped
            self._loop.run_forever()
        finally:
            self._loop.close()
            asyncio.set_event_loop_policy(None)

    def shutdown(self, timeout: float = None):
        async def _shutdown():
            self._running = False
            self._shutdown_start_time = time.perf_counter()

        def is_loop_running(loop):
            return not loop.is_closed() and loop.is_running()

        block = timeout is None
        loop_running = is_loop_running(self._loop)

        _log.debug(
            "%sing thread shutdown requested with%s timeout. State: running (%s, loop running: %s)",
            self._op_type.value,
            f"{timeout}s" if timeout is not None else "out",
            self._running,
            loop_running,
        )

        if not loop_running:
            _log.error("Thread shutdown requested more than once")
            return

        # Initiated shutdown
        future = asyncio.run_coroutine_threadsafe(_shutdown(), loop=self._loop)

        # Wait for thread runner to possibly complete on time.
        if not block:
            self.join(timeout=timeout)

        # Thread possibly still running, force immediate shutdown
        async def _force_shutdown(loop):
            current_task = asyncio.current_task(loop=loop)
            pending_tasks = [t for t in asyncio.all_tasks(loop) if t != current_task]
            if len(pending_tasks) == 0:
                _log.debug("Clean shutdown")
            else:
                for task in pending_tasks:
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task

                results = await asyncio.gather(*pending_tasks, return_exceptions=True)
                _log.debug("finished awaiting cancelled tasks, results: %s", results)

                if not block:
                    _log.warning(
                        "%sing thread took longer than %ss to shutdown",
                        self._op_type.value,
                        timeout,
                    )

            loop.call_soon(loop.stop)

        if is_loop_running(self._loop):
            future = asyncio.run_coroutine_threadsafe(_force_shutdown(self._loop), loop=self._loop)
            future.result(timeout=None)
            _log.warning("%sing thread is now terminated: %s", self._op_type.value, future)

    def _log_thread_status(self, running, operating, dirty_shutdown, shutdown_duration):
        _log.debug(
            "%s. Operating on log records: %s. %s",
            f"{self._op_type.value}ing thread is running" if running else "shutting down",
            {operating},
            (
                f"(Shutdown duration: {shutdown_duration}s, dirty shutdown: {dirty_shutdown})"
                if shutdown_duration is not None
                else ""
            ),
        )

    def _log_thread_started(self):
        _log.debug("%sing thread started", self._op_type.value)

    def _log_thread_stopped(self, duration):
        _log.debug(
            "%sing thread stopped %s",
            {self._op_type.value},
            str(duration) + "s after requested shutdown" if duration is not None else "",
        )
