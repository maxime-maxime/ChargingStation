from enum import Enum


class ReportStatus(Enum):
    """Lifecycle states of a malfunction report"""
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    INVALID = "invalid"
    TICKET_CREATED = "ticket_created"
    RESOLVED = "resolved"
    CLOSED = "closed"