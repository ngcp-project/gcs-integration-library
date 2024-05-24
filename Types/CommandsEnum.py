from dataclasses import dataclass
from Types.Geolocation import Coordinate, Polygon
from enum import Enum, auto
from typing import Any


@dataclass(repr=False)
class CommandsEnum(Enum):
    MANUAL_MODE = "manual"
    TARGET = "target"
    SEARCH_AREA = "search"
    EMERGENCY_STOP = "emergency"
    KEEP_IN = "keepIn"
    KEEP_OUT = "keepOut"