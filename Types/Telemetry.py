from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from typing import Any

from Types.Geolocation import Coordinate


class Status(Enum):
    IN_USE = "In Use"
    STANDBY = "Standby"
    EMERGENCY = "Emergency"


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
        return vars(self)
    
    def to_json(self) -> str:
        tel = vars(self)
        return json.dumps(tel, indent=2)
        





    
    