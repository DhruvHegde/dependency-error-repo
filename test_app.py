import pytest

def test_assertion_mismatch_113():
    expected = 965
    actual = 4883
    assert expected == actual, f"Expected {expected} but got {actual}"
