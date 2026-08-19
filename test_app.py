import pytest

def test_type_mismatch_36():
    result = "string_value" + 109
    assert result is not None
