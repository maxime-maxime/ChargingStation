from enum import Enum


class StationStatus(Enum):
    """Operational status of a charging station"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    DEFECTIVE = "defective"
    MAINTENANCE = "maintenance"