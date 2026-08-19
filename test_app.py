import pytest

def test_type_mismatch_28():
    result = "string_value" + 715
    assert result is not None
