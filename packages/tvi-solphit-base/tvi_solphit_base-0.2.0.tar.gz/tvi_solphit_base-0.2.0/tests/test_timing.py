import time
import logging
from io import StringIO
from tvi.solphit.base.timing import stopwatch, timeit

def _capture_logger(name: str):
    """Return (logger, handler, stream) with a temporary stream handler attached."""
    logger = logging.getLogger(name)
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger, handler, stream

def test_stopwatch_logs_duration():
    logger, handler, stream = _capture_logger("tvi.solphit.timing")
    try:
        with stopwatch("unit-work"):
            time.sleep(0.02)
        handler.flush()
        out = stream.getvalue()
        assert "unit-work took " in out
    finally:
        logger.removeHandler(handler)

def test_timeit_decorator_logs():
    logger, handler, stream = _capture_logger("tvi.solphit.timing")
    try:
        @timeit("decorated")
        def do_work():
            time.sleep(0.01)
            return 42
        val = do_work()
        assert val == 42
        handler.flush()
        out = stream.getvalue()
        assert "decorated took " in out
    finally:
        logger.removeHandler(handler)