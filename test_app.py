import pytest

def test_missing_dict_key_149():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_9744"]
    assert val == True
