from dataclasses import dataclass
from typing import List

@dataclass
class Coordinate:
    latitude: float
    longitude: float


@dataclass
class Polygon:
    coordinates: list[Coordinate]
    