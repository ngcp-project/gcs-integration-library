import asyncio
import nats
import os 
from nats.errors import TimeoutError

class CommandsNATS:
    
    #Creating the object
    def __init__(self, vehicle_name:str, node_name: str): 
        self.vehicle_name = vehicle_name.lower()     
        self.nc = None
        self.node = node_name   
        
    async def setup_NATS(self):
        
        #Setting up the new connection
        servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",") #THE Ip address is always the device itself

        #Connecting to the server
        self.nc = await nats.connect(servers=servers)
        self.node = await self.nc.subscribe(self.node)
        
        
        # Recieving messages
        print("Connection succesful, subscribed to: " + self.vehicle_name)
        while True: 
            try:
                msg = await self.node.next_msg(timeout=3)
                print("Received:", msg)
            except TimeoutError:
                pass