from dataclasses import dataclass
from enum import Enum


@dataclass(repr=False)
class CommandsEnum(Enum):
	manual = "manual"
	target = "target"
	search = "search"
	emergency = "emergency"
	keepIn = "keepIn"
	keepOut = "keepOut"
