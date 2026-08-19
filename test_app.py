import pytest

def test_type_mismatch_143():
    result = "string_value" + 291
    assert result is not None
