from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Coordinate:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "latitude": self.latitude, 
            "longitude": self.longitude
        }


@dataclass
class Polygon:
    coordinates: List[Coordinate]
    def to_dict(self) -> Dict:
        return {
            'coordinates': [vars(coord) for coord in self.coordinates]
        }
    

