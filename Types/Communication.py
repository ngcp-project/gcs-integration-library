from dataclasses import dataclass
from typing import Any, Dict, Optional
from Types.Telemetry import Telemetry
from Types.Commands import Commands
from Types.CommandsEnum import CommandsEnum
class Message:
    def __init__(self, telemetry_data: Optional[Telemetry] = None, commands_data: Optional[Any] = None,
                 vehicle_id: int = 0):  # 1 for Telemetry, 0 for Commands
        self.vId = vehicle_id  # Vehicle ID
        self.tD = telemetry_data  # Telemetry Data
        self.cD = commands_data  # Commands Data

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "vId": self.vId,
            "tD": self.tD.to_dict() if self.tD else None,
            "cD": self.cD
        }
        return {k: v for k, v in data.items() if v is not None}  # Remove `None` values
     