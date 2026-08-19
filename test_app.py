import pytest

def test_missing_dict_key_85():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2474"]
    assert val == True
