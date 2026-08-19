import pytest

def test_type_mismatch_22():
    result = "string_value" + 841
    assert result is not None
