from dataclasses import dataclass
from typing import List, Any

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
    coordinates: list[Coordinate]
    def to_dict(self) -> dict:
        return {
            # 'coordinates': [vars(coord) for coord in self.coordinates]
             'coordinates': [coord.to_dict() for coord in self.coordinates]
        }
    


