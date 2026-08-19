import pytest

def test_missing_dict_key_74():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_1835"]
    assert val == True
