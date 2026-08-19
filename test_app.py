import pytest

def test_type_mismatch_8():
    result = "string_value" + 695
    assert result is not None
