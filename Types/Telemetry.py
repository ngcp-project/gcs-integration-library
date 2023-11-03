from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from Types.Geolocation import Coordinate


class Status(Enum):
    IN_USE = "In Use"
    STANDBY = "Standby"
    EMERGENCY= "Emergency"


@dataclass(repr=False)
class Telemetry:
    pitch: float
    yaw: float
    roll: float
    speed: float
    altitude: float
    batteryLife: float
    currentCoordinate: Coordinate
    vehicleStatus: Status
    lastUpdated: datetime
    
    def to_dict(self) -> dict[str, Any]:
        obj = vars(self)





    
    