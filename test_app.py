import pytest

def test_missing_dict_key_114():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_7274"]
    assert val == True
