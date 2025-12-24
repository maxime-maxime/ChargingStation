import pytest
from uuid import uuid4
from domain.entities.malfunction_report import MalfunctionReport
from domain.value_objects.station_id import StationId
from domain.value_objects.report_description import ReportDescription
from domain.enums.malfunction_type import MalfunctionType
from domain.enums.report_status import ReportStatus


def test_create_malfunction_report():
    """Test creating a basic malfunction report"""
    # Arrange
    report_id = uuid4()
    station_id = StationId("STATION-001")
    description = ReportDescription("Payment terminal not working properly")
    
    # Act
    report = MalfunctionReport(
        report_id=report_id,
        station_id=station_id,
        malfunction_type=MalfunctionType.PAYMENT_FAILURE,
        description=description
    )
    
    # Assert
    assert report.report_id == report_id
    assert report.station_id == station_id
    assert report.status == ReportStatus.SUBMITTED
    assert report.ticket_id is None


def test_validate_report_with_existing_station():
    """Test validating a report when station exists"""
    # Arrange
    report = MalfunctionReport(
        report_id=uuid4(),
        station_id=StationId("STATION-001"),
        malfunction_type=MalfunctionType.NOT_CHARGING,
        description=ReportDescription("Vehicle not charging at all")
    )
    
    # Act
    is_valid = report.validate(station_exists=True, station_is_operational=True)
    
    # Assert
    assert is_valid is True
    assert report.status == ReportStatus.VALIDATED