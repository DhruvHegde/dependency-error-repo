import pytest

def test_type_mismatch_61():
    result = "string_value" + 427
    assert result is not None
