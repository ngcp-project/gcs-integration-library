from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Coordinate:
    latitude: float
    longitude: float
    def to_dict(self) -> dict:
        obj = {
            'latitude' : self.latitude,
            'longitude' : self.longitude,
        }
        return obj


@dataclass
class Polygon:
    coordinates: List[Coordinate]
    def to_dict(self) -> Dict:
        return {
            # 'coordinates': [vars(coord) for coord in self.coordinates]
             'coordinates': [coord.to_dict() for coord in self.coordinates]
        }
    


