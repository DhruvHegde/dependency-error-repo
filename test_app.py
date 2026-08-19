import pytest

def test_type_mismatch_44():
    result = "string_value" + 391
    assert result is not None
