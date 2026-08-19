import pytest

def test_type_mismatch_11():
    result = "string_value" + 384
    assert result is not None
