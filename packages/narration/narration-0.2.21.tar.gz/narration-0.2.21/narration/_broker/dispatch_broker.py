from narration._broker.shared_dispatch import (
    SharedBackgroundDispatch,
    SharedReceiverDispatch,
    SharedSenderDispatch,
)

import threading

from narration._handler.common.misc.op_type import OpType
from narration._handler.common.callable import (
    RecordSignal,
    CallableThreadCreate,
    CallableThreadDestroy,
)

_lock = threading.Lock()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with _lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DispatchBroker(metaclass=Singleton):
    def __init__(self):
        self._dispatchs: dict[str, SharedBackgroundDispatch] = {}
        self._mutex = threading.Lock()

    def _key(self, role_type: OpType = None, group_id: str = None) -> str:
        return f"{role_type.name}-{group_id}"

    def bind(
        self,
        role_type: OpType = None,
        group_id: str = None,
        handler_id: str = None,
        thread_create: CallableThreadCreate = None,
        thread_destroy: CallableThreadDestroy = None,
        record_emitter: RecordSignal = None,
    ) -> SharedBackgroundDispatch:
        with self._mutex:
            key = self._key(role_type=role_type, group_id=group_id)
            dispatch = self._dispatchs.get(key, None)
            existed = dispatch is not None
            if not existed:
                if role_type == OpType.RECEIVE:
                    dispatch = SharedReceiverDispatch(
                        thread_create=thread_create, thread_destroy=thread_destroy
                    )
                elif role_type == OpType.SEND:
                    dispatch = SharedSenderDispatch(
                        thread_create=thread_create, thread_destroy=thread_destroy
                    )
                else:
                    raise NotImplementedError()

                self._dispatchs[key] = dispatch

            dispatch.bind(handler_id=handler_id, record_emitter=record_emitter)
            return dispatch

    def unbind(
        self, role_type: OpType = None, group_id: str = None, handler_id: str = None
    ) -> threading.Event:
        with self._mutex:
            key = self._key(role_type=role_type, group_id=group_id)
            dispatch = self._dispatchs.get(key, None)
            if dispatch is not None:
                dispatch.unbind(handler_id=handler_id)
                if dispatch.usage_count == 0:
                    self._dispatchs.pop(key, None)
                return dispatch.thread.shutdown_completed

            shutdown_completed = threading.Event()
            shutdown_completed.set()
            return shutdown_completed


DISPATCH_BROKER = DispatchBroker()
