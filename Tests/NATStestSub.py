from Commands.NATS import CommandsNATS
import asyncio

async def main():
    
    #Initializing Objects
    testSub = CommandsNATS("uav", "uav")
    
    #Setting Up the Connection
    await testSub.setup_NATS()


#Using ASYNCIO to run main
if __name__ == '__main__':
    #Avoids Eventloop Error
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())