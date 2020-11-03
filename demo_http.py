#!/usr/bin/env python3



import logging
import requests

logging.basicConfig(level=logging.DEBUG)


import retry

global_stats = {}

requests.get = retry.me(requests.get, trigger_method="raise_for_status", stats=global_stats)


if __name__ == "__main__":
    stats = {}
    try:
        print("error code 500 retry allowed")
        result = requests.get("https://httpbin.org/status/500", retries=retry.http_retries(2, stats=stats))
        print(result)
    except Exception as ex:
        print("failed:", ex)
    try:
        print("error code 404 retry useless")
        result = requests.get("https://httpbin.org/status/404", retries=retry.http_retries(2, stats=stats))
        print(result)
    except Exception as ex:
        print("failed:", ex)
    print("stats:", stats)
    print("global stats:", global_stats)
