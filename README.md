# Retry Mechanism for Python

After being slightly appalled by the [suggested retry mechanism for `requests`](https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/#retry-on-failure)
I doodled around a bit and came up with this:

    import retry

    requests.get = retry.me(requests.get, trigger_method="raise_for_status")

    result = requests.get("https://httpbin.org/status/500", retries=retry.http_retries(2))

Works for normal functions as well:

    import random, retry

    def compute_something():
        if random.random() > 0.8:
            raise ValueError("bad result")
        return "actual result"

    compute_something = retry.me(compute_something)

    result = compute_something(retries=3)
