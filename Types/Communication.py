from dataclasses import dataclass
from typing import Any, Dict, Optional
from Types.Telemetry import Telemetry
from Types.Commands import Commands
from Types.CommandsEnum import CommandsEnum


@dataclass
class MessageType:
    dataType: str = ""
    messageType: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'dataType': self.dataType,
            'messageType': self.messageType
        }

@dataclass
class Message:
    vehicleId: int = None
    messageType: MessageType
    telemetryData: Optional[Telemetry] = None
    commandsData: Optional[Commands] = None
    
    def to_dict(self) -> Dict:
        return {
            'vehicleId': self.vehicleId,
            'messageType': self.messageType.to_dict(),
            'telemetryData': self.telemetryData.to_dict(), 
            'commandsData': self.commandsData
        }
     