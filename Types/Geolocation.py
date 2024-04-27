from dataclasses import dataclass
from typing import List

@dataclass
class Coordinate:
    latitude: float
    longitude: float


@dataclass
class Polygon:
    coordinates: List[Coordinate]
    def to_dict(self) -> dict:
        return {
            'coordinates': [vars(coord) for coord in self.coordinates]
        }
    


