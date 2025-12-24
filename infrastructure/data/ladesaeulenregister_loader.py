import csv
from typing import List
from pathlib import Path
from domain.entities.charging_station import ChargingStation
from domain.value_objects.station_id import StationId


class LadesaeulenregisterLoader:
    """Loader for German Ladesaeulenregister CSV format"""
    
    def __init__(self):
        """Initialize loader and find the CSV file"""
        self.csv_path = Path("infrastructure/datasets/Ladesaeulenregister.csv")
        
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found at: {self.csv_path}")
        
        print(f"📂 Found CSV at: {self.csv_path}")
    
    def load_berlin_stations(self) -> List[ChargingStation]:
        """Load all Berlin charging stations"""
        stations = []
        seen_locations = set()
        station_counter = 1
        
        with open(self.csv_path, 'r', encoding='utf-8') as file:
            # Detect delimiter
            sample = file.read(2048)
            file.seek(0)
            delimiter = ';' if sample.count(';') > sample.count(',') else ','
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            print(f"📋 CSV Columns found: {len(reader.fieldnames)} columns")
            
            for row in reader:
                try:
                    # Filter for Berlin
                    ort = row.get('Ort', '').strip()
                    bundesland = row.get('Bundesland', '').strip()
                    
                    if 'Berlin' not in ort and 'Berlin' not in bundesland:
                        continue
                    
                    # Get postal code
                    postal_code = row.get('Postleitzahl', '').strip()
                    if not postal_code:
                        continue
                    
                    # Build address
                    street = row.get('Straße', row.get('Strasse', '')).strip()
                    house_num = row.get('Hausnummer', '').strip()
                    address = f"{street} {house_num}".strip() if street else None
                    
                    # Unique location check
                    location_key = f"{postal_code}-{street}-{house_num}"
                    if location_key in seen_locations:
                        continue
                    seen_locations.add(location_key)
                    
                    # Create name
                    operator = row.get('Betreiber', '').strip()
                    name = operator if operator else f"Station {postal_code}"
                    if len(name) > 100:
                        name = name[:97] + "..."
                    
                    # Get coordinates
                    lat = row.get('Breitengrad', '')
                    lon = row.get('Längengrad', '')
                    
                    latitude = None
                    longitude = None
                    
                    if lat:
                        try:
                            latitude = float(lat.replace(',', '.'))
                        except:
                            pass
                    
                    if lon:
                        try:
                            longitude = float(lon.replace(',', '.'))
                        except:
                            pass
                    
                    # Create station
                    station_id = f"BERLIN-{postal_code}-{station_counter:04d}"
                    station_counter += 1
                    
                    station = ChargingStation(
                        station_id=StationId(station_id),
                        name=name,
                        postal_code=postal_code,
                        address=address,
                        latitude=latitude,
                        longitude=longitude
                    )
                    
                    stations.append(station)
                    
                except Exception:
                    continue
        
        print(f"✅ Loaded {len(stations)} Berlin stations")
        return stations
    
    def get_summary(self) -> dict:
        """Get summary statistics"""
        stations = self.load_berlin_stations()
        
        postal_codes = {}
        for station in stations:
            postal_codes[station.postal_code] = postal_codes.get(station.postal_code, 0) + 1
        
        stations_with_coords = sum(1 for s in stations if s.latitude and s.longitude)
        
        return {
            'total_berlin_stations': len(stations),
            'unique_postal_codes': len(postal_codes),
            'stations_per_postal_code': dict(sorted(postal_codes.items())),
            'stations_with_coordinates': stations_with_coords,
            'coverage_percentage': round((stations_with_coords / len(stations) * 100), 1) if stations else 0
        }
