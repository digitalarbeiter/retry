#!/usr/bin/env python3

import random

import retry

def compute_something(values):
    if random.random() < 0.9:  # unlikely to fail twice in a row
        return sum(values) / len(values)
    else:
        print("failure!")
        raise ValueError("random too high")

if __name__ == "__main__":
    compute_something = retry.me(compute_something)
    values = [1, 2, 3, 4]
    for i in range(20):
        result = compute_something(values, retries=1)
        print("run", i, "-->", result)
