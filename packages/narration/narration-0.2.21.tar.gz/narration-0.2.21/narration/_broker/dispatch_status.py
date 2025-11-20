from concurrent.futures._base import Future
from typing import Any
from collections.abc import Callable


class DispatchStatus:
    def __init__(self, future: Future, payload: Any) -> None:
        self._future = future
        self._payload = payload

    @property
    def future(self) -> Future:
        return self._future

    @property
    def payload(self) -> Any:
        return self._payload

    def emit(self, emitter: Callable = None, drop_completion_if_successful: bool = True) -> None:
        if self.future.done():
            return

        if not self.future.running():
            if not self.future.set_running_or_notify_cancel():
                return

        try:
            result = emitter(self.payload)
            if not drop_completion_if_successful:
                self.future.set_result(result)
        except BaseException as exc:
            self.future.set_exception(exc)
