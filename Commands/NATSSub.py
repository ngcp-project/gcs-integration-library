import asyncio
import nats
import os 
from nats.errors import TimeoutError

class CommandsNATS:
    
    #Creating the object
    def __init__(self):      
        self.nc = None
        self.node = None    
        
    async def setup_NATS(self,node_name):
        
        #Setting up the new connection
        servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")
        #Connecting to the server
        self.nc = await nats.connect(servers=servers)
        self.node = await self.nc.subscribe(node_name)
        
        
        # Recieving messages
        print("Connection succesful, to exit program type 'exit': ")
        while True: 
            try:
                msg = await self.node.next_msg(timeout=3)
                print("Received:", msg)
            except TimeoutError:
                pass