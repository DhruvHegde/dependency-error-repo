import pytest

def test_assertion_mismatch_121():
    expected = 603
    actual = 1280
    assert expected == actual, f"Expected {expected} but got {actual}"
