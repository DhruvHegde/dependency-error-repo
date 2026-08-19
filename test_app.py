import pytest

def test_assertion_mismatch_18():
    expected = 386
    actual = 7982
    assert expected == actual, f"Expected {expected} but got {actual}"
