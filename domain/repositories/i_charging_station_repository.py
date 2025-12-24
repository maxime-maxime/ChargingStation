from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.charging_station import ChargingStation
from domain.value_objects.station_id import StationId


class IChargingStationRepository(ABC):
    """Repository interface for ChargingStation aggregate"""
    
    @abstractmethod
    def save(self, station: ChargingStation) -> None:
        """Save or update a charging station"""
        pass
    
    @abstractmethod
    def find_by_id(self, station_id: StationId) -> Optional[ChargingStation]:
        """Find a station by its ID"""
        pass
    
    @abstractmethod
    def find_by_postal_code(self, postal_code: str) -> List[ChargingStation]:
        """Find all stations in a postal code area"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[ChargingStation]:
        """Get all charging stations"""
        pass
    
    @abstractmethod
    def exists(self, station_id: StationId) -> bool:
        """Check if a station exists"""
        pass