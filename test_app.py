import pytest

def test_type_mismatch_11():
    result = "string_value" + 116
    assert result is not None
