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
<<<<<<< HEAD
    vehicleStatus: Status
    lastUpdated: datetime
    fireFound: bool
    vehicleSearch: Coordinate
=======
    lastUpdated: datetime
    fireFound: bool
    fireCoordinate: Coordinate
>>>>>>> 10ac9f9ced53dc25ffe59d6c7220daff3c5acd67
    
    def to_dict(self) -> Dict[str, Any]:
        obj = {
            'localIP': self.localIP,
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll':self.roll,
            'speed':self.speed,
            'altitude': self.altitude,
            'batteryLife':self.batteryLife,
            'currentCoordinate': vars(self.currentPosition),
<<<<<<< HEAD
            'vehicleStatus': self.vehicleStatus.value,
            'lastUpdated': self.lastUpdated.timestamp(),
            'fireFound': self.fireFound,
            'vehicleSearch': vars(self.vehicleSearch)
=======
            'lastUpdated': self.lastUpdated.timestamp(),
            'fireFound': self.fireFound,
            'fireCoordinate': vars(self.vehicleSearch)
>>>>>>> 10ac9f9ced53dc25ffe59d6c7220daff3c5acd67
        }
        return obj





    
    
