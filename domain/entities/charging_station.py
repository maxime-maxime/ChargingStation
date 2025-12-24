from datetime import datetime
from typing import Optional
from domain.value_objects.station_id import StationId
from domain.enums.station_status import StationStatus


class ChargingStation:
    """
    Entity: Charging Station
    Represents a physical EV charging station with operational status
    """
    
    def __init__(
        self,
        station_id: StationId,
        name: str,
        postal_code: str,
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ):
        self._station_id = station_id
        self._name = name
        self._postal_code = postal_code
        self._address = address
        self._latitude = latitude
        self._longitude = longitude
        self._status = StationStatus.AVAILABLE
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def station_id(self) -> StationId:
        return self._station_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def postal_code(self) -> str:
        return self._postal_code
    
    @property
    def address(self) -> Optional[str]:
        return self._address
    
    @property
    def latitude(self) -> Optional[float]:
        return self._latitude
    
    @property
    def longitude(self) -> Optional[float]:
        return self._longitude
    
    @property
    def status(self) -> StationStatus:
        return self._status
    
    @property
    def is_operational(self) -> bool:
        """Check if station is operational (available or in use)"""
        return self._status in [StationStatus.AVAILABLE, StationStatus.IN_USE]
    
    def mark_as_defective(self) -> None:
        """Mark station as defective due to malfunction report"""
        if self._status == StationStatus.DEFECTIVE:
            raise ValueError("Station already marked as defective")
        
        self._status = StationStatus.DEFECTIVE
        self._updated_at = datetime.now()
    
    def mark_as_available(self) -> None:
        """Restore station to available status after repair"""
        if self._status != StationStatus.DEFECTIVE:
            raise ValueError("Can only restore defective stations to available")
        
        self._status = StationStatus.AVAILABLE
        self._updated_at = datetime.now()