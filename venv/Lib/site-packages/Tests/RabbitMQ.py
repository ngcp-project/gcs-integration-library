import time
from datetime import datetime
# from Telemetry.RabbitMQ import TelemetryRabbitMQ
# from Types.Geolocation import Coordinate
# from Types.Telemetry import Telemetry

if __name__ == '__main__':
    telemetry = TelemetryRabbitMQ(
            "ERU",      # Topic name for this sample: 'telemetry_eru'
            "localhost" # Change to IP of the RabbitMQ broker host machine
        )
    try:
        while True:
            data = Telemetry(
                pitch=10.5,
                yaw=20.3,
                roll=5.8,
                speed=45.2,
                altitude=1000.0,
                batteryLife=80.5,
                currentCoordinate=Coordinate(
                    latitude=37.7749, 
                    longitude=-122.4194
                ),
                lastUpdated=datetime.now()
            )
            
            telemetry.publish(data) # Data will now be published to all subcribers of 'telemetry_eru'
            print("[*] Data successfully published!")
            time.sleep(0.5)         # Half second sleep delay. Remove if you wanna stress test it!
            
    
    except Exception as e:
        telemetry.close_connection()
        raise e
    