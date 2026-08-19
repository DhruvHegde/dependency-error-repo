import pytest

def test_type_mismatch_46():
    result = "string_value" + 129
    assert result is not None
