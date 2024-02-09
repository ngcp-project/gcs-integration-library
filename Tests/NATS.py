from ..Telemetry.NATS import *
from ..Types.Telemetry import *
import asyncio

async def main():
    
    #Initializing Object
    test = TelemetryNATS()
    
    #Setting Up the Connection
    await test.setup_NATS()
    
    #Publishing Vehicle Data
    while True:   
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
            vehicleStatus=Status.IN_USE
        )
        await test.publish_NATS("foo",tel.pitch,tel.yaw,tel.roll,)


        


#Using ASYNCIO to run main
if __name__ == '__main__':
    #Avoids Eventloop Error
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())