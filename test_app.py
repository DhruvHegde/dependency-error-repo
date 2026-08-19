import pytest

def test_missing_dict_key_29():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_3667"]
    assert val == True
