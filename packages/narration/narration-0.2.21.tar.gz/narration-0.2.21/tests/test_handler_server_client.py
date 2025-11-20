import logging
import multiprocessing as mp
import os
import random
import re
import signal
import unittest
from io import StringIO

from pyexpect import expect

from narration.narration import teardown_handlers, logger_dispatch_remaining_messages
from narration.constants import Backend
from tests.setup_logger import _create_client_logger, _create_server_logger
from tests.utils import yield_to_other_threads, wait_processes

import time


def assert_no_exception_on_logging_shutdown():
    try:
        logging.shutdown()
    except BaseException as e:
        assert e is not None, f"Logging shutdown failed: {e}"  # nosec B101


# Child process workers, for some unit tests
def _worker_it_should_pass_all_logs(wid, client_handler_settings, log_record_count):
    logger = _create_client_logger(client_handler_settings=client_handler_settings)
    for i in range(log_record_count):
        logger.info("Worker %d log record %d.", wid, i)
    logger_dispatch_remaining_messages(loggers=[logger])
    assert_no_exception_on_logging_shutdown()


def _worker_records_should_not_be_garbled(
    wid, client_handler_settings, log_record_count, wait_time
):
    logger = _create_client_logger(client_handler_settings=client_handler_settings)
    for i in range(log_record_count):
        logger.info("Worker %d started. Log record %d", wid, i)
        logger.info("Worker %d finished dispatching. Log record %d", wid, i)
    logger_dispatch_remaining_messages(loggers=[logger])
    assert_no_exception_on_logging_shutdown()


def _worker_child_process_terminate_abruptly(wid, client_handler_settings, log_record_count):
    logger = _create_client_logger(client_handler_settings=client_handler_settings)
    for i in range(log_record_count):
        if i == log_record_count:
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            logger.info("Worker %d log record %d", wid, i)
    # Process "crashed". Hence:
    # logger_dispatch_remaining_messages(loggers=[logger]) will not be called
    # assert_no_exception_on_logging_shutdown() will not be called


def _worker_client_congested(wid, client_handler_settings, log_record_count):
    logger = _create_client_logger(client_handler_settings=client_handler_settings)
    for i in range(log_record_count):
        logger.info("Worker %d log. Log record %d", wid, i)

    logger_dispatch_remaining_messages(loggers=[logger])
    assert_no_exception_on_logging_shutdown()


class TestConcurrentProcessesLogRecords:
    def setup_method(self, method):
        self.loggers = []

    def teardown_method(self, method):
        teardown_handlers(loggers=self.loggers, timeout=None)

    def teardown_at_test_exit(self, logger: logging.Logger) -> None:
        self.loggers.append(logger)

    # @pytest.mark.timeout(30)
    # @pytest.mark.skip
    def test_receive_last_record_emitted(self, backend: Backend) -> None:
        stream = StringIO()
        logger_m0, m0_client_handler_settings = _create_server_logger(
            orignal_handler=logging.StreamHandler(stream=stream), backend=backend
        )
        logger_m0.setLevel(logging.DEBUG)
        self.teardown_at_test_exit(logger_m0)

        logger_c0 = _create_client_logger(client_handler_settings=m0_client_handler_settings)
        self.teardown_at_test_exit(logger_c0)
        logger_c0.info("Last record.")

        yield_to_other_threads(duration=1.5)

        expect("Last record.\n").to_equal(stream.getvalue())

    # @pytest.mark.timeout(60)
    # @pytest.mark.skip
    def test_pass_all_logs(self, backend: Backend) -> None:
        stream = StringIO()
        logger_m0, m0_client_handler_settings = _create_server_logger(
            orignal_handler=logging.StreamHandler(stream=stream), backend=backend
        )

        logger_m0.setLevel(logging.DEBUG)
        self.teardown_at_test_exit(logger_m0)

        logger_m0.info("Creating workers...")
        worker_count = 2
        record_count = 10
        processes = [
            mp.Process(
                target=_worker_it_should_pass_all_logs,
                args=(wid, m0_client_handler_settings, record_count),
            )
            for wid in range(worker_count)
        ]
        for proc in processes:
            proc.start()
        logger_m0.info("Workers started.")

        wait_processes(processes=processes)
        logger_m0.info("Workers destroyed.")

        yield_to_other_threads(duration=0.5)

        stream.seek(0)
        lines = stream.readlines()
        expect("Creating workers...\n").within(lines)
        expect("Workers started.\n").within(lines)
        expect("Workers destroyed.\n").within(lines)
        expect(len(lines)).to_equal(len(set(lines)))
        expect(3 + worker_count * record_count).to_equal(len(lines))

    # @pytest.mark.timeout(60)
    # @pytest.mark.skip
    def test_child_process_terminated_abruptly(self, backend: Backend) -> None:
        stream = StringIO()
        logger_m0, m0_client_handler_settings = _create_server_logger(
            orignal_handler=logging.StreamHandler(stream=stream), backend=backend
        )

        logger_m0.setLevel(logging.DEBUG)
        self.teardown_at_test_exit(logger_m0)

        logger_m0.info("Creating workers...")
        worker_count = 2
        record_count = 10
        processes = [
            mp.Process(
                target=_worker_child_process_terminate_abruptly,
                args=(wid, m0_client_handler_settings, record_count),
            )
            for wid in range(worker_count)
        ]
        for proc in processes:
            proc.start()
        logger_m0.info("Workers started.")

        wait_processes(processes=processes)
        logger_m0.info("Workers destroyed.")

        yield_to_other_threads(duration=0.5)

        stream.seek(0)
        lines = stream.readlines()
        expect("Creating workers...\n").within(lines)
        expect("Workers started.\n").within(lines)
        expect("Workers destroyed.\n").within(lines)
        expect(len(lines)).to_equal(len(set(lines)))
        expect(len(lines)).between(3, 3 + worker_count * record_count)

    # @pytest.mark.timeout(120)
    # @pytest.mark.skip
    def test_records_in_emitting_order_over_multiplexed_handlers(self, backend: Backend) -> None:
        stream_m0 = StringIO()
        logger_m0, m0_client_handler_settings = _create_server_logger(
            orignal_handler=logging.StreamHandler(stream=stream_m0), backend=backend
        )
        stream_m1 = StringIO()
        logger_m1, m1_client_handler_settings = _create_server_logger(
            orignal_handler=logging.StreamHandler(stream=stream_m1), backend=backend
        )

        for logger_m, client_handler_settings, stream in [
            (logger_m0, m0_client_handler_settings, stream_m0),
            (logger_m1, m1_client_handler_settings, stream_m1),
        ]:
            logger_m.setLevel(logging.DEBUG)
            self.teardown_at_test_exit(logger_m)

            logger_m.info("Creating workers...")
            worker_count = 10
            record_count = 10
            processes = [
                mp.Process(
                    target=_worker_records_should_not_be_garbled,
                    args=(
                        wid,
                        client_handler_settings,
                        record_count,
                        random.random(),  # nosec B311
                    ),
                )
                for wid in range(worker_count)
            ]
            for proc in processes:
                proc.start()

            logger_m.info("Workers started.")

            wait_processes(processes=processes, timeout=record_count * 1.1)
            yield_to_other_threads(duration=10.0)

            logger_m.info("Workers destroyed.")

            stream.seek(0)
            lines = stream.readlines()
            expect("Creating workers...\n").within(lines)
            expect("Workers started.\n").within(lines)
            expect("Workers destroyed.\n").within(lines[-1])
            expect(len(lines)).to_equal(len(set(lines)))

            valid_line = re.compile(
                r"(?:Creating workers...)"
                r"|(?:Worker \d+ started\. Log record \d+)"
                r"|(?:Workers started\.)"
                r"|(?:Worker \d+ finished dispatching\. Log record \d+)"
                r"|(?:Workers destroyed.)"
            )

            expect(3 + 2 * worker_count * record_count).to_equal(len(lines))
            for line in lines:
                expect(re.match(valid_line, line))

    # @pytest.mark.timeout(60)
    # @pytest.mark.skip
    def test_pass_congested_client(self, backend: Backend) -> None:
        stream = StringIO()
        logger_m0, m0_client_handler_settings = _create_server_logger(
            orignal_handler=logging.StreamHandler(stream=stream), backend=backend
        )

        logger_m0.setLevel(logging.DEBUG)
        self.teardown_at_test_exit(logger_m0)
        # Sleep to allow for log thread sender to have time to work ?
        time.sleep(0.1)
        logger_m0.info("Creating workers...")
        worker_count = 1
        record_count = 100
        processes = [
            mp.Process(
                target=_worker_client_congested,
                args=(wid, m0_client_handler_settings, record_count),
            )
            for wid in range(worker_count)
        ]
        for proc in processes:
            proc.start()
        logger_m0.info("Workers started.")

        wait_processes(processes=processes, timeout=None)
        logger_m0.info("Workers destroyed.")

        yield_to_other_threads(duration=0.5)

        stream.seek(0)
        lines = stream.readlines()
        expect("Creating workers...\n").within(lines)
        expect("Workers started.\n").within(lines)
        expect("Workers destroyed.\n").within(lines)
        expect(len(lines)).to_equal(len(set(lines)))
        expect(3 + worker_count * record_count).to_equal(len(lines))

    def test_always_last_test(self, backend: Backend) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
