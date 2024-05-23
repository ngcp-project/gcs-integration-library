from dataclasses import dataclass
from Types.Geolocation import Coordinate, Polygon
from enum import Enum, auto
from typing import Any


@dataclass(repr=False)
class CommandsEnum(Enum):
    manual = "manual"
    target = "target"
    search = "search"
    emergency = "emergency"
    keepIn = "keepIn"
    keepOut = "keepOut"