import pytest
from src.shared.application.postal_code import PostalCode

def test_valid_berlin_postal_code():
    pc = PostalCode("10115")
    assert pc.value == "10115"

def test_postal_code_must_be_numeric():
    with pytest.raises(ValueError) as e:
        PostalCode("ABCDE")
    print("ERR : ", str(e.value))

def test_postal_code_must_have_five_digits():
    with pytest.raises(ValueError) as e:
        PostalCode("1011")

def test_postal_code_must_be_berlin():
    with pytest.raises(ValueError) as e:
        PostalCode("75001")
    print("ERR : ", str(e.value))