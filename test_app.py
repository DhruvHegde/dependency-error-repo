import pytest

def test_missing_dict_key_55():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_8806"]
    assert val == True
