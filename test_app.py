import pytest

def test_type_mismatch_24():
    result = "string_value" + 774
    assert result is not None
