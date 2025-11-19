"""Tests for pytimer core functions."""

import time
from pylib-timer import Timer, timeit


def test_timer():
    with Timer() as t:
        time.sleep(0.1)
    assert t.elapsed > 0


@timeit
def test_function():
    time.sleep(0.01)
    return True


def test_timeit():
    assert test_function() is True
