from dataclasses import dataclass
from Types.Geolocation import Coordinate, Polygon
<<<<<<< HEAD
from enum import Enum, auto
from typing import Any
=======
from typing import Dict
>>>>>>> 10ac9f9ced53dc25ffe59d6c7220daff3c5acd67


@dataclass(repr=False)
class Commands:
    isManual: bool
    emergencyStop: bool
    target: Coordinate
    searchArea: Polygon
    keepIn: Polygon
    keepOut: Polygon
    

    def to_dict(self) -> Dict:
        obj = {
            'isManual': self.isManual,
<<<<<<< HEAD
            'target': self.target.to_dict(),
            'searchArea': self.searchArea.to_dict(),
=======
            'emergencyStop': self.emergencyStop,
            'target': vars(self.target),
            'searchArea':self.searchArea.to_dict(),
            'keepIn': self.keepIn.to_dict(),
            'keepOut': self.keepOut.to_dict()
>>>>>>> 10ac9f9ced53dc25ffe59d6c7220daff3c5acd67
        }
        return obj
