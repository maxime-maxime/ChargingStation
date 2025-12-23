import pytest
from src.shared.domain.postal_code import PostalCode

def test_postal_code_validation():

    pc = PostalCode("10115")
    assert pc.value == "10115"

    with pytest.raises(ValueError) as e:
        PostalCode("ABCDE")
    print("ERR : ", str(e.value))

    with pytest.raises(ValueError) as e:
        PostalCode("1011")
    print("ERR : ", str(e.value))

    with pytest.raises(ValueError) as e:
        PostalCode("75001")
    print("ERR : ", str(e.value))

    with pytest.raises(ValueError) as e:
        PostalCode("10116")
    print("ERR : ", str(e.value))