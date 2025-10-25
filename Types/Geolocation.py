from dataclasses import dataclass
from typing import List, Dict

class Coordinate:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def to_dict(self) -> Dict[str, float]:
        return {"lat": self.lat, "lon": self.lon}


class Polygon:
    def __init__(self, coordinates: List[Coordinate]):
        self.coord = coordinates

    def to_dict(self) -> Dict:
        return {"coord": [coord.to_dict() for coord in self.coord]}

