import pytest

def test_type_mismatch_136():
    result = "string_value" + 825
    assert result is not None
