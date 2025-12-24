import pytest
from uuid import uuid4
from domain.entities.charging_station import ChargingStation
from domain.entities.malfunction_report import MalfunctionReport
from domain.value_objects.station_id import StationId
from domain.value_objects.report_description import ReportDescription
from domain.enums.malfunction_type import MalfunctionType
from infrastructure.repositories.in_memory_charging_station_repository import (
    InMemoryChargingStationRepository
)
from infrastructure.repositories.in_memory_malfunction_report_repository import (
    InMemoryMalfunctionReportRepository
)


class TestInMemoryChargingStationRepository:
    """Test in-memory implementation of station repository"""
    
    @pytest.fixture
    def repository(self):
        """Create a fresh repository for each test"""
        return InMemoryChargingStationRepository()
    
    @pytest.fixture
    def sample_station(self):
        """Create a sample station for testing"""
        return ChargingStation(
            station_id=StationId("STATION-001"),
            name="Test Station",
            postal_code="10178"
        )
    
    def test_save_and_find_station(self, repository, sample_station):
        """Test saving and retrieving a station"""
        repository.save(sample_station)
        found = repository.find_by_id(sample_station.station_id)
        
        assert found is not None
        assert found.station_id == sample_station.station_id
        assert found.name == sample_station.name
    
    def test_find_nonexistent_station_returns_none(self, repository):
        """Test finding a station that doesn't exist"""
        found = repository.find_by_id(StationId("NONEXISTENT"))
        assert found is None
    
    def test_exists_returns_true_for_saved_station(self, repository, sample_station):
        """Test exists method returns True for saved station"""
        repository.save(sample_station)
        exists = repository.exists(sample_station.station_id)
        assert exists is True
    
    def test_find_by_postal_code(self, repository):
        """Test finding stations by postal code"""
        station1 = ChargingStation(
            station_id=StationId("STATION-001"),
            name="Station 1",
            postal_code="10178"
        )
        station2 = ChargingStation(
            station_id=StationId("STATION-002"),
            name="Station 2",
            postal_code="10178"
        )
        station3 = ChargingStation(
            station_id=StationId("STATION-003"),
            name="Station 3",
            postal_code="10785"
        )
        
        repository.save(station1)
        repository.save(station2)
        repository.save(station3)
        
        stations_10178 = repository.find_by_postal_code("10178")
        
        assert len(stations_10178) == 2
        assert all(s.postal_code == "10178" for s in stations_10178)


class TestInMemoryMalfunctionReportRepository:
    """Test in-memory implementation of report repository"""
    
    @pytest.fixture
    def repository(self):
        """Create a fresh repository for each test"""
        return InMemoryMalfunctionReportRepository()
    
    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing"""
        return MalfunctionReport(
            report_id=uuid4(),
            station_id=StationId("STATION-001"),
            malfunction_type=MalfunctionType.NOT_CHARGING,
            description=ReportDescription("Test malfunction report")
        )
    
    def test_save_and_find_report(self, repository, sample_report):
        """Test saving and retrieving a report"""
        repository.save(sample_report)
        found = repository.find_by_id(sample_report.report_id)
        
        assert found is not None
        assert found.report_id == sample_report.report_id
    
    def test_find_reports_by_station(self, repository):
        """Test finding all reports for a specific station"""
        station_id = StationId("STATION-001")
        report1 = MalfunctionReport(
            report_id=uuid4(),
            station_id=station_id,
            malfunction_type=MalfunctionType.NOT_CHARGING,
            description=ReportDescription("First report")
        )
        report2 = MalfunctionReport(
            report_id=uuid4(),
            station_id=station_id,
            malfunction_type=MalfunctionType.PAYMENT_FAILURE,
            description=ReportDescription("Second report")
        )
        
        repository.save(report1)
        repository.save(report2)
        
        station_reports = repository.find_by_station(station_id)
        
        assert len(station_reports) == 2