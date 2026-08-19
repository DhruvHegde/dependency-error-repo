import pytest

def test_type_mismatch_10():
    result = "string_value" + 818
    assert result is not None
