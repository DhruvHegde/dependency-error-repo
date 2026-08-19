import pytest

def test_type_mismatch_97():
    result = "string_value" + 840
    assert result is not None
