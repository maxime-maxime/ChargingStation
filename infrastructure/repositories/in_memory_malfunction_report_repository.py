from typing import Optional, List, Dict
from uuid import UUID
from domain.entities.malfunction_report import MalfunctionReport
from domain.value_objects.station_id import StationId
from domain.repositories.i_malfunction_report_repository import IMalfunctionReportRepository


class InMemoryMalfunctionReportRepository(IMalfunctionReportRepository):
    """In-memory implementation of malfunction report repository"""
    
    def __init__(self):
        """Initialize empty storage"""
        self._reports: Dict[UUID, MalfunctionReport] = {}
    
    def save(self, report: MalfunctionReport) -> None:
        """Save or update a malfunction report"""
        self._reports[report.report_id] = report
    
    def find_by_id(self, report_id: UUID) -> Optional[MalfunctionReport]:
        """Find a report by its ID"""
        return self._reports.get(report_id)
    
    def find_by_station(self, station_id: StationId) -> List[MalfunctionReport]:
        """Find all reports for a specific station"""
        return [
            report for report in self._reports.values()
            if report.station_id == station_id
        ]
    
    def find_all(self) -> List[MalfunctionReport]:
        """Get all reports"""
        return list(self._reports.values())