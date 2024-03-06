import asyncio
import nats
import os 
from nats.errors import TimeoutError

class CommandsNATS:
    
    #Creating the object
    def __init__(self):      
        self.connection = None
        self.node_name = None 
        self.subscriber = None   
        
    async def setup_NATS(self,node_name):
        
        print("Attempting to connect...")

        #Setting up the new connection
        servers = os.environ.get("NATS_URL", "nats://127.0.0.1:4222").split(",")


        #Connecting to the server
        self.connection = await nats.connect(servers=servers,)
        self.node_name = node_name
        self.subscriber = await self.connection.subscribe(node_name) #Used to wait for the next message before sending another
        print("Succesfully connected to: " + str(servers))
        
        # Recieving messages
        print("Connection succesful, to exit program type 'exit': ")
        while True: 
            try:
                msg = await self.subscriber.next_msg(timeout=3)
                command = msg.data.decode("utf-8")
                print("Received:", command)
            except TimeoutError:
                pass