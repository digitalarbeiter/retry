#!/usr/bin/env python3


import retry


class CountDown:
    def __init__(self, start):
        self.n = self.start = start
    def count_down(self):
        self.n -= 1
        if self.n > 0:
            raise ValueError("not there yet")
        return "countdown started at {}".format(self.start)


if __name__ == "__main__":
    print("without retry:")
    counter = CountDown(3)
    try:
        result = counter.count_down()
        print(result)
    except Exception as ex:
        print("failed:", ex)

    print("with retry:")
    counter = CountDown(3)
    counter.count_down = retry.me(counter.count_down)
    try:
        result = counter.count_down(retries=2)
        print(result)
    except Exception as ex:
        print("failed:", ex)
