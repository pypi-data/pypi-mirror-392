import re
import time
from threading import Event
from collections.abc import Callable


class RetryAbortedByCheck(Exception):
    pass


def sleep(duration: int, check: Callable | None = None, step: float = 1.0) -> bool:
    end = time.time() + duration
    rest = duration
    while rest > 0:
        if check is not None and check():
            return True

        if rest > step:
            time.sleep(step)
            rest = end - time.time()
        elif rest <= 0:
            return False
        else:
            time.sleep(rest)
            return False

    return False


def retry(
    exceptions: BaseException = BaseException,
    tries: int = 3,
    backoff_factor: float = 1,
    check: Callable = None,
    retry_log: Callable = None,
):
    """

    :param float: backoff_factor: time sleep between retires is calculated with
        ``duration = backoff_factor * 2 ** (retries - 1)``
    :param callable: check: A function / callable that is called on before every
        retry attempt. If value returned by ``check()`` evaluates to true,
        then ``retry`` raises a ``RetryAbortedByCheck`` exception.
    :param callable: retry_log: A function / callable that is called before
        every retry attempt and on the last trial error. The function must
        accept the arguments ``retry_log(trial, last_trial=False)``
    :param exceptions: Default value = Exception)
    :param tries: Default value = 3)
    :param backoff_factor: Default value = 1)
    :param check: Default value = None)
    :param retry_log: Default value = None)

    """
    assert tries >= 0
    assert backoff_factor >= 0

    def wrap(fun):
        def deco(*args, **kwargs):
            last_trial = tries - 1
            for trial in range(tries):
                try:
                    return fun(*args, **kwargs)
                except exceptions as exc:
                    is_last_trial = trial == last_trial

                    if retry_log is not None:
                        retry_log(trial, last_trial=is_last_trial)

                    if is_last_trial:
                        raise

                    duration = backoff_factor * 2 ** (tries - 1)

                    check_succeeds = sleep(duration, check)
                    if check_succeeds:
                        raise RetryAbortedByCheck() from exc

        deco.__name__ = fun.__name__

        return deco

    return wrap


def wait_for_event(event: Event, duration: int, check: Callable, step: float = 0.1) -> None:
    def f():
        if event.is_set():
            return True

        event.wait(step)

        if event.is_set():
            return True

        if not check():
            return True

    sleep(duration, check=f, step=0.01)

    if not event.is_set():
        raise RuntimeError("Thread could not be created")


def requires_random_bind(address: str = None) -> bool:
    """

    :param address: return: False if address does not start with tcp://, False if address contains a port number. True otherwise

    """
    if not address.startswith("tcp://"):
        return False

    if re.search(r":\d+$", address):
        return False

    return True
