import pytest

def test_type_mismatch_78():
    result = "string_value" + 734
    assert result is not None
