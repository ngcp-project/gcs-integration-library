from dataclasses import dataclass
from Types.Geolocation import Coordinate, Polygon
from typing import Any


@dataclass(repr=False)
class Commands:
    # islocalIp: str
    isManual: bool
    target: Coordinate
    searchArea: Polygon

    def to_dict(self) -> dict[str, Any]:
        obj = {
            'isManual': self.isManual,
            'target': self.target.to_dict(),
            'searchArea': self.searchArea.to_dict(),
        }
        return obj

    
    