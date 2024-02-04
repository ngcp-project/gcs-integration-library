from datetime import datetime
from Types.Geolocation import Coordinate
from Types.Telemetry import Status, Telemetry


tel = Telemetry(
    pitch=6.0,
    yaw=0.2,
    roll=1.2,
    speed=1.0,
    altitude=5.0,
    batteryLife=1.2,
    currentCoordinate=Coordinate(
        latitude=30,
        longitude=60
    ),
    vehicleStatus=Status.IN_USE,
    lastUpdated=datetime.now()
)

print(tel.to_json())