import pytest
from src.discovery.domain.services.test_station import validate_PC

def test_postalCode_validation():
    assert validate_PC("00000") == False
    assert validate_PC("10399") == False
    assert validate_PC("10115") == True

