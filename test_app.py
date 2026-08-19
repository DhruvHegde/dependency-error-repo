import pytest

def test_missing_dict_key_54():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_3769"]
    assert val == True
