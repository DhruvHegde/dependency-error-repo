import pytest

def test_missing_dict_key_1():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_1268"]
    assert val == True
