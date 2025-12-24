from typing import Optional, List, Dict
from domain.entities.charging_station import ChargingStation
from domain.value_objects.station_id import StationId
from domain.repositories.i_charging_station_repository import IChargingStationRepository


class InMemoryChargingStationRepository(IChargingStationRepository):
    """In-memory implementation of charging station repository"""
    
    def __init__(self):
        """Initialize empty storage"""
        self._stations: Dict[str, ChargingStation] = {}
    
    def save(self, station: ChargingStation) -> None:
        """Save or update a charging station"""
        key = station.station_id.value
        self._stations[key] = station
    
    def find_by_id(self, station_id: StationId) -> Optional[ChargingStation]:
        """Find a station by its ID"""
        return self._stations.get(station_id.value)
    
    def find_by_postal_code(self, postal_code: str) -> List[ChargingStation]:
        """Find all stations in a postal code area"""
        return [
            station for station in self._stations.values()
            if station.postal_code == postal_code
        ]
    
    def find_all(self) -> List[ChargingStation]:
        """Get all charging stations"""
        return list(self._stations.values())
    
    def exists(self, station_id: StationId) -> bool:
        """Check if a station exists"""
        return station_id.value in self._stations