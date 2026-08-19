import pytest

def test_type_mismatch_72():
    result = "string_value" + 973
    assert result is not None
