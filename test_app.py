import pytest

def test_type_mismatch_18():
    result = "string_value" + 172
    assert result is not None
