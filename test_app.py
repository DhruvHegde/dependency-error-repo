import pytest

def test_missing_dict_key_32():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_1745"]
    assert val == True
