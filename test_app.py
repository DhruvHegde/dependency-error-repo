import pytest

def test_assertion_mismatch_87():
    expected = 236
    actual = 9557
    assert expected == actual, f"Expected {expected} but got {actual}"
