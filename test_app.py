import pytest

def test_missing_dict_key_36():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_3917"]
    assert val == True
