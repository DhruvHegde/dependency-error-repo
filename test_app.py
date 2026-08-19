import pytest

def test_missing_dict_key_52():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_6163"]
    assert val == True
