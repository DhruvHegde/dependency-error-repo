import pytest

def test_assertion_mismatch_105():
    expected = 791
    actual = 4326
    assert expected == actual, f"Expected {expected} but got {actual}"
