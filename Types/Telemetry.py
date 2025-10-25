from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from Types.Geolocation import Coordinate
    
class RequestCoordinates:
    def __init__(self, request_location: Optional[Coordinate] = None,
                 patient_secured: Optional[int] = 1,
                 message_flag: Optional[int] = None):
        self.rL = request_location  # Request Location
        self.pS = patient_secured  # 1 for YES, 0 for NO
        self.mF = message_flag  # 1 = Package, 2 = Patient

    def to_dict(self) -> Dict[str, Any]:
        data = {"mF": self.mF, "rL": self.rL.to_dict() if self.rL else None}
        if self.mF == 2 and self.pS is not None:
            data["pS"] = self.pS  # Only include `patientSecured` if it's relevant
        return data


class Telemetry:
    def __init__(self, speed: float = 0.0, pitch: float = 0.0, yaw: float = 0.0,
                 roll: float = 0.0, alt: float = 0.0, battery_life: float = 0.0,
                 current_position: Optional[Coordinate] = None, last_updated: Optional[datetime] = None,
                 vehicle_status: int = 0, request_coord: Optional[RequestCoordinates] = None):
        self.s = int(speed)  # Convert to integer if possible
        self.p = int(pitch)
        self.y = int(yaw)
        self.r = int(roll)
        self.a = int(alt)
        self.bL = int(battery_life)
        self.cP = current_position  # Current Position
        self.lU = int(last_updated.timestamp()) if last_updated else None  # Store as UNIX timestamp
        self.vS = vehicle_status  # Vehicle Status
        self.rC = request_coord  # Request Coordinates

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "s": self.s, "p": self.p, "y": self.y, "r": self.r, "a": self.a, "bL": self.bL,
            "cP": self.cP.to_dict() if self.cP else None, "lU": self.lU, "vS": self.vS,
            "rC": self.rC.to_dict() if self.rC else None
        }
        return {k: v for k, v in data.items() if v is not None}  # Remove `None` values






    
    
