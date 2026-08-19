import pytest

def test_missing_dict_key_120():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_8787"]
    assert val == True
