from dataclasses import dataclass

from Types.Geolocation import Coordinate, Polygon


@dataclass
class Commands:
    localIp: str
    isManual: bool
    target: Coordinate
    searchArea: Polygon
    
from dataclasses import dataclass

from Types.Geolocation import Coordinate, Polygon


@dataclass
class Commands:
    localIp: str
    isManual: bool
    target: Coordinate
    searchArea: Polygon
    