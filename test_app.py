import pytest

def test_assertion_mismatch_30():
    expected = 742
    actual = 2868
    assert expected == actual, f"Expected {expected} but got {actual}"
