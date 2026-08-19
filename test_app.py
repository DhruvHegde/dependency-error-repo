import pytest

def test_missing_dict_key_92():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_5396"]
    assert val == True
