import logging
import types

from nexios.logging import LocalQueueHandler, create_logger, has_level_handler


def test_create_logger_returns_logger():
    logger = create_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


def test_logger_has_level_handler():
    logger = create_logger("test_logger2")
    assert has_level_handler(logger)


def test_local_queue_handler_prepare():
    handler = LocalQueueHandler(None)
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "msg", (), None)
    assert handler.prepare(record) is record
