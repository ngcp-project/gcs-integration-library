from datetime import datetime
from Telemetry.NATS import TelemetryNATS
from Commands.NATS import CommandsNATS
from Types.Telemetry import Telemetry
import asyncio
import time
import sys

from Types.Geolocation import Coordinate

async def main():
    
    #Initializing Objects
    testPub = TelemetryNATS("uav","uav")
    
    #Setting Up the Connection
    await testPub.setup_NATS("localhost")
    
    #Sending the Data.
    print("Running")
    while (True):

        try:
            #Updating the class Data
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
                lastUpdated=datetime.now()
                
            )

            #Publishing the data
            await testPub.publish_NATS(tel)
            time.sleep(1)
        except Exception as e:
            print(f"An error occurred: {e}")
            testPub.close_NATS()
            raise e

#Using ASYNCIO to run main
if __name__ == '__main__':
    #Avoids Eventloop Error
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())