from __future__ import annotations
import time
from contextlib import contextmanager
from .logging import SolphitLogger

log = SolphitLogger.get_logger("tvi.solphit.timing")

@contextmanager
def stopwatch(label: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = time.perf_counter() - t0
        log.info(f"{label} took {dt:.3f}s")

def timeit(label: str):
    def deco(fn):
        def wrapper(*a, **kw):
            with stopwatch(label):
                return fn(*a, **kw)
        return wrapper
    return deco