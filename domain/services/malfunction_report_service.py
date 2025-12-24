from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID, uuid4
from domain.entities.malfunction_report import MalfunctionReport
from domain.value_objects.station_id import StationId
from domain.value_objects.report_description import ReportDescription
from domain.enums.malfunction_type import MalfunctionType
from domain.repositories.i_charging_station_repository import IChargingStationRepository
from domain.repositories.i_malfunction_report_repository import IMalfunctionReportRepository


@dataclass
class ProcessingResult:
    """Result of processing a malfunction report"""
    success: bool
    ticket_id: Optional[UUID]
    errors: List[str]


class MalfunctionReportService:
    """
    Domain Service: Orchestrates malfunction report workflow
    
    Use cases:
    1. Submit malfunction report
    2. Process/validate report
    3. Resolve malfunction
    """
    
    def __init__(
        self,
        report_repository: IMalfunctionReportRepository,
        station_repository: IChargingStationRepository
    ):
        """Initialize service with required repositories"""
        self._report_repository = report_repository
        self._station_repository = station_repository
    
    def submit_malfunction_report(
        self,
        station_id: str,
        malfunction_type: MalfunctionType,
        description: str,
        reported_by: Optional[str] = None
    ) -> UUID:
        """
        Use Case 1: Submit a new malfunction report
        
        Args:
            station_id: ID of the charging station
            malfunction_type: Type of malfunction
            description: Detailed description
            reported_by: Email of reporter (optional)
        
        Returns:
            UUID of the created report
        """
        # Create value objects (validation happens here)
        station_id_vo = StationId(station_id)
        description_vo = ReportDescription(description)
        
        # Create report entity
        report_id = uuid4()
        report = MalfunctionReport(
            report_id=report_id,
            station_id=station_id_vo,
            malfunction_type=malfunction_type,
            description=description_vo,
            reported_by=reported_by
        )
        
        # Save report
        self._report_repository.save(report)
        
        return report_id
    
    def process_malfunction_report(self, report_id: UUID) -> ProcessingResult:
        """
        Use Case 2: Process and validate malfunction report
        
        This method:
        1. Validates the report
        2. Creates a ticket if valid
        3. Marks station as defective
        
        Args:
            report_id: UUID of the report to process
        
        Returns:
            ProcessingResult with success status and ticket ID
        """
        # Load report
        report = self._report_repository.find_by_id(report_id)
        if not report:
            return ProcessingResult(
                success=False,
                ticket_id=None,
                errors=[f"Report {report_id} not found"]
            )
        
        # Check if station exists and is operational
        station = self._station_repository.find_by_id(report.station_id)
        station_exists = station is not None
        station_is_operational = station.is_operational if station else False
        
        # Validate report (business rules)
        is_valid = report.validate(station_exists, station_is_operational)
        
        if not is_valid:
            # Save invalid report
            self._report_repository.save(report)
            return ProcessingResult(
                success=False,
                ticket_id=None,
                errors=report.get_validation_errors()
            )
        
        # Create ticket
        ticket_id = uuid4()
        report.create_ticket(ticket_id)
        
        # Mark station as defective
        station.mark_as_defective()
        
        # Save all changes
        self._report_repository.save(report)
        self._station_repository.save(station)
        
        return ProcessingResult(
            success=True,
            ticket_id=ticket_id,
            errors=[]
        )
    
    def resolve_malfunction(
        self,
        ticket_id: UUID,
        operator_notes: Optional[str] = None
    ) -> None:
        """
        Use Case 3: Resolve a malfunction and restore station
        
        Args:
            ticket_id: UUID of the ticket to resolve
            operator_notes: Notes from operator about resolution
        """
        # Find report by ticket ID
        all_reports = self._report_repository.find_all()
        report = next(
            (r for r in all_reports if r.ticket_id == ticket_id),
            None
        )
        
        if not report:
            raise ValueError(f"No report found with ticket ID {ticket_id}")
        
        # Load station
        station = self._station_repository.find_by_id(report.station_id)
        if not station:
            raise ValueError(f"Station {report.station_id} not found")
        
        # Mark report as resolved
        report.resolve()
        
        # Restore station to available
        station.mark_as_available()
        
        # Save changes
        self._report_repository.save(report)
        self._station_repository.save(station)
    
    def get_reports_for_station(self, station_id: str) -> List[MalfunctionReport]:
        """Get all reports for a specific station"""
        station_id_vo = StationId(station_id)
        return self._report_repository.find_by_station(station_id_vo)
    
    def get_all_reports(self) -> List[MalfunctionReport]:
        """Get all malfunction reports"""
        return self._report_repository.find_all()