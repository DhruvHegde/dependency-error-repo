import pytest

def test_assertion_mismatch_13():
    expected = 688
    actual = 9467
    assert expected == actual, f"Expected {expected} but got {actual}"
