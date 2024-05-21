from datetime import datetime
from Telemetry.RabbitMQ import TelemetryRabbitMQ
from Types.Telemetry import Telemetry
from Types.Geolocation import Coordinate
import time

tel = TelemetryRabbitMQ("ERU", "localhost")

data = Telemetry(
    pitch=160,
    yaw=10.34,
    roll=-45.2,
    speed=101.02,
    altitude=0.0,
    batteryLife=0.45,
    currentCoordinate=Coordinate(latitude=34.15, longitude=101.45),
    lastUpdated=datetime.now()
)

while True:
    # Add your telemetry changes here by referring to the attributes in the `data` object
    tel.publish(data)
    time.sleep(2)