from Commands import NATS_Sub
import asyncio

async def main():
    
    #Initializing Objects
    testSub = NATS_Sub.CommandsNATS()
    
    #Setting Up the Connection
    await testSub.setup_NATS("foo")


#Using ASYNCIO to run main
if __name__ == '__main__':
    #Avoids Eventloop Error
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())