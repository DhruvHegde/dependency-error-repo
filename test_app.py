import pytest

def test_assertion_mismatch_89():
    expected = 692
    actual = 2791
    assert expected == actual, f"Expected {expected} but got {actual}"
