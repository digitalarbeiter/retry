#!/usr/bin/env python3
""" Unit tests for trigger functions. (Trigger methods see HTTP tests.)
"""

import pytest

import retry


def exitcode_to_exception(result):
    """ Turn erroneous exitcode into an exception.
    """
    if result != 0:
        raise ValueError("command failed: {}".format(result))


def execute_command(cmd):
    """ (Fake) execution of a Unix command, returns (fake) exit code.
    """
    if cmd == "/bin/true":
        return 0  # 0 means success
    return 1  # failure


execute_command = retry.me(execute_command, trigger_function=exitcode_to_exception)


def test_trigger_function():
    """ Test if trigger function (turning error exit codes to exceptions)
        work.
    """
    with pytest.raises(ValueError):
        execute_command("/bin/false", retries=2)
    exit_code = execute_command("/bin/true", retries=1)
    assert exit_code == 0
