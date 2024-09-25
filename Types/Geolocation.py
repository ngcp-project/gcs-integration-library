from dataclasses import dataclass


@dataclass
class Coordinate:
	latitude: float
	longitude: float


@dataclass
class Polygon:
	coordinates: list[Coordinate]

	def to_dict(self) -> dict:
		return {"coordinates": [vars(coord) for coord in self.coordinates]}
