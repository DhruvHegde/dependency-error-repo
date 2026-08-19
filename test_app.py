import pytest

def test_missing_dict_key_67():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2321"]
    assert val == True
