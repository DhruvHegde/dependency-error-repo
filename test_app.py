import pytest

def test_assertion_mismatch_112():
    expected = 655
    actual = 7206
    assert expected == actual, f"Expected {expected} but got {actual}"
