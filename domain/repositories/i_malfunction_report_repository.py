from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from domain.entities.malfunction_report import MalfunctionReport
from domain.value_objects.station_id import StationId


class IMalfunctionReportRepository(ABC):
    """Repository interface for MalfunctionReport aggregate"""
    
    @abstractmethod
    def save(self, report: MalfunctionReport) -> None:
        """Save or update a malfunction report"""
        pass
    
    @abstractmethod
    def find_by_id(self, report_id: UUID) -> Optional[MalfunctionReport]:
        """Find a report by its ID"""
        pass
    
    @abstractmethod
    def find_by_station(self, station_id: StationId) -> List[MalfunctionReport]:
        """Find all reports for a specific station"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[MalfunctionReport]:
        """Get all reports"""
        pass