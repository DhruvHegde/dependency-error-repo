import pytest

def test_assertion_mismatch_42():
    expected = 317
    actual = 1286
    assert expected == actual, f"Expected {expected} but got {actual}"
