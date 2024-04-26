from dataclasses import dataclass
from Types.Geolocation import Coordinate, Polygon
from typing import Any


@dataclass
class Commands:
    # islocalIp: str
    isManual: bool
    target: Coordinate
    searchArea: Polygon

    def to_dict(self) -> dict:
        obj = {
            'isManual': self.isManual,
            'target': vars(self.target),
            'searchArea':self.searchArea.to_dict()
        }
        return obj
    
    
