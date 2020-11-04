#!/usr/bin/env python3
# coding: utf-8
""" Retries Decorator.
"""

import logging
import time

_LOG = logging.getLogger(__name__)


class n_retries:  # pylint: disable=invalid-name,old-style-class,too-few-public-methods
    """ Retry up to n times, regardless of what error occured.
    """
    def __init__(self, n):
        """ Retry up to n times, regardless of what error occured.

            @param n (int) maximum number of retries.
        """
        self.n = n + 1

    def __call__(self, _exception, _result):
        self.n -= 1
        return bool(self.n)


class http_retries:  # pylint: disable=invalid-name,old-style-class,too-few-public-methods
    """ Retry up to n times, with special logic for HTTP requests.
    """
    def __init__(self, n, retry_on_http_status=(429, 500, 502, 503, 504), delay=0.0, stats=None):
        """ Retry up to n times, with special logic for HTTP requests.

            For per call statistics, pass a dict as `stats` and check its
            `"retries"` value afterwards. For global stats (i.e. _all_ calls
            to the original function) see `retry.me(..., stats)` param.

            @param n (int) maximum number of retries.
            @param retry_on_http_status (list of int) retry on these HTTP
                status codes only.
            @param delay (float) delay in seconds before retry.
            @param stats (dict) count number of retries in stats["retries"].
        """
        self.n = n + 1
        self.retry_on_http_status = retry_on_http_status
        self.delay = delay
        self.stats = stats if stats is not None else {}

    def __call__(self, _exception, result):
        self.n -= 1
        if not self.n:
            return False
        if (
                result is None
                or not self.retry_on_http_status
                or result.status_code in self.retry_on_http_status
        ):
            _LOG.debug("retrying in %s seconds...", self.delay)
            time.sleep(self.delay)
            self.stats["retries"] = self.stats.get("retries", 0) + 1
            return True
        return False


def me(function, default_retries=None, trigger_method=None, trigger_function=None, stats=None):  # pylint: disable=invalid-name
    """ Decorator retry.me(function)

        This decorates the original function and allows it to accept a new
        keyword argument `retries` which controls whether or not a function
        call should be retried (default: no retries). The `retries` argument
        may be an integer or something more complex, see for example
        `http_retries`.

        Thus decorated, the original function is called with the given
        arguments, and the result is passed back, unless one of these is
        true...
         - the original function raises an exception
         - calling trigger_method on the result raises an exception
         - calling trigger_function with the result raises an exception

        If an exception occurs, the `retries` argument of the function call is
        evaluated with the exception and the result (is any) of the original
        function. Should `retries()` evaluate to True, another attempt is made
        and the cycle repeats itself.

        For global stats (i.e. all calls to the original function), pass a
        dict as `stats` and check its `"retries"` value afterwards.
        For per call statistics, see `http_retries(..., stats)` param.

        @param function (callable) the function/method to be retried on error.
        @param default_retries (int) by default retry this many times.
        @param trigger_method (str) if given, this method is called on the
            result object of the original function.
        @param trigger_function (callable) if given, this function is called
            with the result of the original function.
        @param stats (dict) count number of retries in stats["retries"].
    """
    if stats is None:  # `if stats:` would overwrite a passed in empty dict
        stats = {}
    def _inner(*args, **kwargs):
        retries = kwargs.pop("retries", default_retries) or 0
        if not retries:
            # no retries, so just forge ahead with the original function
            return function(*args, **kwargs)
        if isinstance(retries, int):
            # convenience: make a n_retries instance of the integer
            retries = n_retries(retries)
        while True:
            result = None
            try:
                result = function(*args, **kwargs)
                if trigger_method:
                    getattr(result, trigger_method)()
                if trigger_function:
                    trigger_function(result)
                return result
            except Exception as exception:  # pylint: disable=broad-except
                # exception may stem from original function *or* one of the
                # triggers, so maybe we do have a result != None
                if not retries(exception, result):
                    raise
                _LOG.debug("error %r, retrying...", exception)
                stats["retries"] = stats.get("retries", 0) + 1
    return _inner
