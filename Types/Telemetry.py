from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from Types.Geolocation import Coordinate

@dataclass(repr=False)
class StatusEnum(Enum):
    SAFE = 1
    NOT_SAFE = 0
    
@dataclass(repr=False)
class RequestCoordinates:
    messageFlag: Optional[int] # 1 = Package, 2 = Patient
    requestLocation: Optional[Coordinate] = None
    patientSecured: Optional[StatusEnum] = field(default_factory=lambda: StatusEnum.NOT_SAFE)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "messageFlag": self.messageFlag,
            "requestLocation": self.requestLocation.to_dict() if self.requestLocation else None,
            "patientSecured": self.patientSecured if self.messageFlag == 2 else None
        }

@dataclass(repr=False)
class Telemetry:
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0
    speed: float = 0.0
    altitude: float = 0.0
    batteryLife: float = 0.0
    currentPosition: Coordinate = None
    lastUpdated: datetime = None
    vehicleStatus: int = 0
    requestCoord: Optional[RequestCoordinates] = None
    
    def send_telemetry(self): pass
    
    def to_dict(self) -> Dict[str, Any]:
        obj = {
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll':self.roll,
            'speed':self.speed,
            'altitude': self.altitude,
            'batteryLife':self.batteryLife,
            'currentPosition': vars(self.currentPosition),
            'lastUpdated': int(self.lastUpdated.timestamp()*1000) if self.lastUpdated else None,
            'requestCoord': self.requestCoord.to_dict() if self.requestCoord else None
        }
        return obj


# ON RUST SIDE

# queue listening for commands ack message from vehicle to GCS
{
    "connectionStatus": 1 # for connected, 0 for disconnected
}




    
    
