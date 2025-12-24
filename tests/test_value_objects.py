import pytest
from domain.value_objects.station_id import StationId
from domain.value_objects.report_description import ReportDescription


def test_create_valid_station_id():
    """Test that we can create a station ID"""
    # Arrange (setup)
    station_id_string = "STATION-001"
    
    # Act (do the thing)
    station_id = StationId(station_id_string)
    
    # Assert (check it worked)
    assert station_id.value == "STATION-001"


def test_empty_station_id_raises_error():
    """Test that empty station ID is rejected"""
    with pytest.raises(ValueError):
        StationId("")
        
def test_station_id_is_immutable():
    """Test that station ID cannot be changed after creation"""
    station_id = StationId("STATION-001")
    
    # Try to change it (should fail)
    with pytest.raises(Exception):  # frozen dataclass raises error
        station_id.value = "STATION-002"


def test_whitespace_only_station_id_raises_error():
    """Test that whitespace-only ID is rejected"""
    with pytest.raises(ValueError):
        StationId("   ")


def test_station_id_too_long_raises_error():
    """Test maximum length validation"""
    with pytest.raises(ValueError):
        StationId("A" * 51)  # More than 50 characters
        
        
def test_create_valid_description():
    """Test creating a valid report description"""
    description = ReportDescription("Station not charging my vehicle properly")
    assert "not charging" in description.value


def test_description_too_short_raises_error():
    """Test minimum length validation"""
    with pytest.raises(ValueError, match="too short"):
        ReportDescription("Bad")


def test_description_too_long_raises_error():
    """Test maximum length validation"""
    with pytest.raises(ValueError, match="too long"):
        ReportDescription("A" * 501)


def test_empty_description_raises_error():
    """Test empty description rejection"""
    with pytest.raises(ValueError):
        ReportDescription("")