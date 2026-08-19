import pytest

def test_assertion_mismatch_44():
    expected = 287
    actual = 2378
    assert expected == actual, f"Expected {expected} but got {actual}"
