from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from Types.Geolocation import Coordinate

@dataclass(repr=False)
class StatusEnum(Enum):
    TBD = 2
    SAFE = 1
    NOT_SAFE = 0
    
@dataclass(repr=False)
class RequestCoordinates:
    requestLocation: Optional[Coordinate] = None
    requestDescription: str = ""
    patientSecured: StatusEnum = field(default_factory=lambda: StatusEnum.TBD)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requestLocation": self.requestLocation.to_dict() if self.requestLocation else None,
            "requestDescription": self.requestDescription,
            "patientSecured": self.patientSecured.name
        }

@dataclass(repr=False)
class Telemetry:
    localIP: str = ""
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0
    speed: float = 0.0
    altitude: float = 0.0
    batteryLife: float = 0.0
    currentPosition: Coordinate = None
    lastUpdated: datetime = None
    fireFound: bool = False
    requestCoord: Optional[RequestCoordinates] = None
    
    def send_telemetry(self): pass
    
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
            'lastUpdated': int(self.lastUpdated.timestamp()*1000) if self.lastUpdated else None,
            'fireFound': self.fireFound,
            'requestCoord': self.requestCoord.to_dict() if self.requestCoord else None
        }
        return obj







    
    
