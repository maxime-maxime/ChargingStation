from enum import Enum


class MalfunctionType(Enum):
    """Types of malfunctions users can report"""
    NOT_CHARGING = "not_charging"
    PAYMENT_FAILURE = "payment_failure"
    PAYMENT_NOT_REFLECTED = "payment_not_reflected"
    PHYSICAL_DAMAGE = "physical_damage"
    DISPLAY_MALFUNCTION = "display_malfunction"
    CONNECTOR_ISSUE = "connector_issue"
    OTHER = "other"
    
    def __str__(self):
        """Human-readable string"""
        return self.value.replace('_', ' ').title()