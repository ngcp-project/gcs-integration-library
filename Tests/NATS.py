from Telemetry import NATS
from Types import Telemetry
import asyncio

from Types.Geolocation import Coordinate

async def main():
    
    #Initializing Object
    test = NATS.TelemetryNATS()
    
    #Setting Up the Connection
    await test.setup_NATS()
    
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
        vehicleStatus=Telemetry.Status.IN_USE
    )
    await test.publish_NATS("foo",tel)


        


#Using ASYNCIO to run main
if __name__ == '__main__':
    #Avoids Eventloop Error
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())