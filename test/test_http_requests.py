#!/usr/bin/env python3
""" Unit tests for HTTP requests.get() retry.
"""

import pytest
import requests

import retry


requests.get = retry.me(requests.get, trigger_method="raise_for_status")


def test_requests_temporary_error():
    """ Status code 500 is worth a retry.
    """
    stats = {}
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get("https://httpbin.org/status/500", retries=retry.http_retries(2, stats=stats))
    assert stats.get("retries", 0) == 2  # 500, so retry twice, the maximum


def test_requests_permanent_error():
    """ Status code 404 is NOT worth retrying.
    """
    stats = {}
    with pytest.raises(requests.exceptions.HTTPError):
        requests.get("https://httpbin.org/status/404", retries=retry.http_retries(2, stats=stats))
    assert stats.get("retries", 0) == 0  # 404 is not retried
