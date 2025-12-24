from uuid import UUID
from datetime import datetime
from typing import Optional
from domain.value_objects.station_id import StationId
from domain.value_objects.report_description import ReportDescription
from domain.enums.malfunction_type import MalfunctionType
from domain.enums.report_status import ReportStatus


class MalfunctionReport:
    """
    Entity: Malfunction Report
    Represents a user-submitted report about a station malfunction
    """
    
    def __init__(
        self,
        report_id: UUID,
        station_id: StationId,
        malfunction_type: MalfunctionType,
        description: ReportDescription,
        reported_by: Optional[str] = None
    ):
        self._report_id = report_id
        self._station_id = station_id
        self._malfunction_type = malfunction_type
        self._description = description
        self._reported_by = reported_by
        self._status = ReportStatus.SUBMITTED
        self._ticket_id: Optional[UUID] = None
        self._created_at = datetime.now()
        self._validation_errors: list[str] = []
    
    @property
    def report_id(self) -> UUID:
        """Get report ID"""
        return self._report_id
    
    @property
    def station_id(self) -> StationId:
        """Get station ID"""
        return self._station_id
    
    @property
    def status(self) -> ReportStatus:
        """Get current status"""
        return self._status
    
    @property
    def ticket_id(self) -> Optional[UUID]:
        """Get associated ticket ID"""
        return self._ticket_id
    
    def validate(self, station_exists: bool, station_is_operational: bool) -> bool:
        """
        Validate the report against business rules
        
        Args:
            station_exists: Whether the station exists in the system
            station_is_operational: Whether the station is available/in-use (not defective)
        
        Returns:
            True if valid, False otherwise
        """
        self._validation_errors.clear()
        
        # Business Rule 1: Station must exist
        if not station_exists:
            self._validation_errors.append("Charging station does not exist")
        
        # Business Rule 2: Station should not already be defective
        if not station_is_operational:
            self._validation_errors.append("Station already marked as defective")
        
        # Update status based on validation
        if self._validation_errors:
            self._status = ReportStatus.INVALID
            return False
        
        self._status = ReportStatus.VALIDATED
        return True
    
    def get_validation_errors(self) -> list[str]:
        """Get validation error messages"""
        return self._validation_errors.copy()
    
    def create_ticket(self, ticket_id: UUID) -> None:
        """
        Create a ticket for this validated report
        
        Args:
            ticket_id: UUID of the ticket being created
        
        Raises:
            ValueError: If report is not validated
        """
        if self._status != ReportStatus.VALIDATED:
            raise ValueError("Cannot create ticket for non-validated report")
        
        self._ticket_id = ticket_id
        self._status = ReportStatus.TICKET_CREATED
        self._updated_at = datetime.now()
    
    def resolve(self) -> None:
        """
        Mark the report as resolved
        
        Raises:
            ValueError: If report doesn't have a ticket
        """
        if self._ticket_id is None:
            raise ValueError("Cannot resolve report without a ticket")
        
        self._status = ReportStatus.RESOLVED
        self._updated_at = datetime.now()