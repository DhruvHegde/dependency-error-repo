import pytest

def test_type_mismatch_98():
    result = "string_value" + 499
    assert result is not None
