import pytest

def test_missing_dict_key_64():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_6810"]
    assert val == True
