from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from Types.Geolocation import Coordinate

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
    vehicleStatus: Any
    lastUpdated: datetime
    fireFound: bool
    vehicleSearch: Coordinate
    lastUpdated: datetime
    fireFound: bool
    fireCoordinate: Coordinate
    
    def to_dict(self) -> Dict[str, Any]:
        obj = {
            'localIP': self.localIP,
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll':self.roll,
            'speed':self.speed,
            'altitude': self.altitude,
            'batteryLife':self.batteryLife,
            'currentPosition': vars(self.currentPosition),
            'vehicleStatus': str(self.vehicleStatus),
            'lastUpdated': self.lastUpdated.timestamp(),
            'fireFound': self.fireFound,
            'vehicleSearch': vars(self.vehicleSearch),
            'lastUpdated': self.lastUpdated.timestamp() * 1000,
            'fireFound': self.fireFound,
            'fireCoordinates': vars(self.fireCoordinate)
        }
        return obj





    
    
