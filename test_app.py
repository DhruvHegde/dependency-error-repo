import pytest

def test_type_mismatch_45():
    result = "string_value" + 448
    assert result is not None
