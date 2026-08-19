import pytest

def test_type_mismatch_28():
    result = "string_value" + 813
    assert result is not None
