from datetime import datetime
from Telemetry import NATSPub
from Commands import NATSSub
from Types import Telemetry
import asyncio
import time
import sys

from Types.Geolocation import Coordinate

async def main():
    
    #Initializing Objects
    testPub = NATSPub.TelemetryNATS()
    
    #Setting Up the Connection
    await testPub.setup_NATS("foo","localhost")

    #Updating the class Data
    tel = Telemetry.Telemetry(
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
        vehicleStatus=Telemetry.Status.IN_USE,
        lastUpdated=datetime.now()
        
    )
    
    #Sending the Data.
    print("Running")
    while (True):
        await testPub.publish_NATS(tel)
        time.sleep(5)
    





#Using ASYNCIO to run main
if __name__ == '__main__':
    #Avoids Eventloop Error
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())