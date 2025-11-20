import logging
import multiprocessing as mp
from unittest import mock

from pyexpect import expect

from narration._handler.server.common.handler.base_server_handler import BaseServerHandler
from narration.narration import teardown_handlers
from tests.setup_logger import _create_server_logger
from tests.utils import new_logger_name
from collections.abc import Callable


def _assert_result(
    logger: logging.Logger | None = None, handler: logging.NullHandler | None = None
) -> None:
    handlers = list(filter(lambda h: isinstance(h, BaseServerHandler), logger.handlers))
    expect(handlers[0]).instance_of(BaseServerHandler)
    handlers = list(filter(lambda h: not isinstance(h, BaseServerHandler), logger.handlers))
    expect(handlers[0]).to_be(handler)


class TestHandlerInstallation:
    def setup_method(self, method: Callable) -> None:
        self.handler = logging.NullHandler()
        self.logger = None

    def teardown_method(self, method):
        teardown_handlers(loggers=[self.logger], timeout=None)

    # @pytest.mark.timeout(10)
    # @pytest.mark.skip
    def test_provided_logger(self, backend: None = None) -> None:
        ctx = mp.get_context()
        m = ctx.Manager()

        name = new_logger_name(prefix="root")
        logger = logging.getLogger(name)

        with mock.patch("logging.getLogger", create=True) as mocked_logger:
            mocked_logger.return_value = logger
            self.logger, _ = _create_server_logger(
                logger=logger, orignal_handler=self.handler, ctx=ctx, ctx_manager=m, backend=backend
            )

            expect(0).to_equal(mocked_logger.call_count)

    # @pytest.mark.timeout(10)
    # @pytest.mark.skip
    def test_logger_has_all_handlers_wrapped(self, backend: None = None) -> None:
        ctx = mp.get_context()
        m = ctx.Manager()
        self.logger, _ = _create_server_logger(
            orignal_handler=self.handler, ctx=ctx, ctx_manager=m, backend=backend
        )

        _assert_result(logger=self.logger, handler=self.handler)
