from dataclasses import dataclass
from Types.Geolocation import Coordinate, Polygon
from enum import Enum, auto
from typing import Any


@dataclass(repr=False)
class CommandsEnum(Enum):
    MANUAL_MODE = "manual"
    TARGET = "target"
    SEARCH_AREA = "search_area"
    EMERGENCY_STOP = "emergency_stop"
    KEEP_IN = "keep_in"
    KEEP_OUT = "keep_out"