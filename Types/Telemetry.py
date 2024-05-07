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
    localIP: str
    pitch: float
    yaw: float
    roll: float
    speed: float
    altitude: float
    batteryLife: float
    currentPosition: Coordinate
    vehicleStatus: Status
    lastUpdated: datetime
    fireFound: bool
    vehicleSearch: Coordinate
    
    def to_dict(self) -> dict[str, Any]:
        obj = {
            'localIP': self.localIP,
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll':self.roll,
            'speed':self.speed,
            'altitude': self.altitude,
            'batteryLife':self.batteryLife,
            'currentCoordinate': vars(self.currentPosition),
            'vehicleStatus': self.vehicleStatus.value,
            'lastUpdated': self.lastUpdated.timestamp(),
            'fireFound': self.fireFound,
            'vehicleSearch': vars(self.vehicleSearch)
        }
        return obj





    
    