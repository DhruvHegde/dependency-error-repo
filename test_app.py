import pytest

def test_type_mismatch_6():
    result = "string_value" + 814
    assert result is not None
