import pytest

def test_assertion_mismatch_86():
    expected = 201
    actual = 9629
    assert expected == actual, f"Expected {expected} but got {actual}"
