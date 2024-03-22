from Telemetry.RabbitMQ import TelemetryRabbitMQ
from Types.Telemetry import Status, Telemetry
from Types.Geolocation import Coordinate
from datetime import datetime
import time

if __name__ == "__main__":
    # vehicle_name = input("Enter vehicle name: ")
    telemetry = TelemetryRabbitMQ("ERU")
    coordinate = Coordinate(latitude=37.7749, longitude=-122.4194)
    while True:
        data = Telemetry(
        pitch=10.5,
        yaw=20.3,
        roll=5.8,
        speed=45.2,
        altitude=1000.0,
        batteryLife=80.5,
        currentCoordinate=coordinate,
        vehicleStatus=Status.IN_USE,
        lastUpdated=datetime.now()
        )
        print(data.to_dict())
        time.sleep(10)
    # telemetry_data = {
    #     "speed": 60,
    #     "temperature": 25,
    #     "location": "42.3601° N, 71.0589° W"
    # }
    # try:
    #     publisher.publish(telemetry_data)
    # finally:
    #     publisher.close_connection()