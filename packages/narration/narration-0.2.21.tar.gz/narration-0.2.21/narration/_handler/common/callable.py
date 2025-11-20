import threading
from collections.abc import Callable

import blinker

RecordSignal = blinker.Signal
CallableThreadCreate = Callable[[], None]
CallableThreadDestroy = Callable[[threading.Thread], None]
