import pytest

def test_type_mismatch_39():
    result = "string_value" + 892
    assert result is not None
