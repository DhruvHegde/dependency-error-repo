import pytest

def test_missing_dict_key_16():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_4274"]
    assert val == True
