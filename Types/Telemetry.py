from dataclasses import dataclass
from datetime import datetime
from typing import Any

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
	lastUpdated: datetime
	fireFound: bool
	fireCoordinate: Coordinate

	def to_dict(self) -> dict[str, Any]:
		obj = {
			"localIP": self.localIP,
			"pitch": self.pitch,
			"yaw": self.yaw,
			"roll": self.roll,
			"speed": self.speed,
			"altitude": self.altitude,
			"batteryLife": self.batteryLife,
			"currentCoordinate": vars(self.currentPosition),
			"lastUpdated": self.lastUpdated.timestamp(),
			"fireFound": self.fireFound,
			"fireCoordinate": vars(self.fireCoordinate),
		}
		return obj
