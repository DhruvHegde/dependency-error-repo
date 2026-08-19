import pytest

def test_missing_dict_key_37():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_4041"]
    assert val == True
