import pytest

def test_assertion_mismatch_141():
    expected = 604
    actual = 3178
    assert expected == actual, f"Expected {expected} but got {actual}"
