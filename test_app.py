import pytest

def test_missing_dict_key_26():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_6365"]
    assert val == True
