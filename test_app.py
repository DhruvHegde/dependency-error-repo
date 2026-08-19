import pytest

def test_assertion_mismatch_102():
    expected = 383
    actual = 2739
    assert expected == actual, f"Expected {expected} but got {actual}"
