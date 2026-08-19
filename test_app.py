import pytest

def test_missing_dict_key_133():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_1026"]
    assert val == True
