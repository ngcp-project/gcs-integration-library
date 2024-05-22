from dataclasses import dataclass
from Types.Geolocation import Coordinate, Polygon
from typing import Dict


@dataclass
class Commands:
    # islocalIp: str
    isManual: bool
    emergencyStop: bool
    target: Coordinate
    searchArea: Polygon
    keepIn: Polygon
    keepOut: Polygon
    

    def to_dict(self) -> Dict:
        obj = {
            'isManual': self.isManual,
            'emergencyStop': self.emergencyStop,
            'target': vars(self.target),
            'searchArea':self.searchArea.to_dict(),
            'keepIn': self.keepIn.to_dict(),
            'keepOut': self.keepOut.to_dict()
        }
        return obj
    
    