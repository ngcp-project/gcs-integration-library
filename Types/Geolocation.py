from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Coordinate:
    latitude: float
    longitude: float


@dataclass
class Polygon:
    coordinates: List[Coordinate]

    def to_dict(self) -> Dict:
        return {"coordinates": [vars(coord) for coord in self.coordinates]}
