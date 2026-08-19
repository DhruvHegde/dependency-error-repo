import pytest

def test_type_mismatch_23():
    result = "string_value" + 114
    assert result is not None
