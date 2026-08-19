import pytest

def test_type_mismatch_144():
    result = "string_value" + 235
    assert result is not None
