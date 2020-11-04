#!/usr/bin/env python3
""" Unit tests for default retries (in decorator).
"""

import random

import retry


def average(values):
    """ Compute average of values, with a 10% failure chance.
    """
    if random.random() < 0.9:  # unlikely to fail twice in a row
        return sum(values) / len(values)
    else:
        print("failure!")
        raise ValueError("random too high")


average = retry.me(average, default_retries=1)


def test_default_retries():
    """ Test if default retries works.
    """
    values = [1, 2, 3, 4]
    for _ in range(20):
        result = average(values)
        assert result == 2.5
