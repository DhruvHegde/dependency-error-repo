import pytest

def test_missing_dict_key_145():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2045"]
    assert val == True
