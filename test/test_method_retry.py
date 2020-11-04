#!/usr/bin/env python3
""" Unit tests for method retries.
"""

import pytest

import retry


class CountDown:
    """ Class that raises exceptions the first calls.
    """
    def __init__(self, start):
        """ @param start (int) countdown from this.
        """
        self.n = self.start = start

    def count_down(self):
        """ Raises ValueError the first n calls, then returns n.
        """
        self.n -= 1
        if self.n > 0:
            raise ValueError("not there yet")
        return self.start


def test_without_decorator():
    counter = CountDown(3)
    with pytest.raises(ValueError):
        counter.count_down()


def test_without_retries():
    counter = CountDown(3)
    counter.count_down = retry.me(counter.count_down)
    with pytest.raises(ValueError):
        counter.count_down()


def test_enough_retries():
    counter = CountDown(3)
    counter.count_down = retry.me(counter.count_down)
    result = counter.count_down(retries=10)
    assert result == 3


def test_not_enough_retries():
    counter = CountDown(3)
    counter.count_down = retry.me(counter.count_down)
    with pytest.raises(ValueError):
        counter.count_down(retries=1)
