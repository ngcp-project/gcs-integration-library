import os
import json
import nats
from nats.errors import TimeoutError
import asyncio

class TelemetryNATS:
        
    #Creating the object
    #@params: vehicle_name = name of the vehicle | node_name = name of the node you are publishing to
    def __init__(self, vehicle_name: str, node_name: str):      
        self.connection = None 
        self.node_name = node_name
        self.subscriber = None
        self.vehicle_name = vehicle_name.lower()
   
    #Setting up the connection
    #@params: ipv4 = ip address of the SUBSCRIBER
    async def setup_NATS(self,ipv4: str):
        print("Attempting to connect...")

        #Setting up the new connection
        nats_server = "nats://" + ipv4 + ":4222"
        servers = os.environ.get("NATS_URL", nats_server).split(",")

        #Connecting to the server
        self.connection = await nats.connect(servers=servers,)
        self.subscriber = await self.connection.subscribe(self.node_name) #Used to wait for the next message before sending another

        print(str(self.vehicle_name) + " has succesfully connected to: " + str(servers) + " and is publishing to: " + self.node_name)
        
    #Function to run the telemetry connection.
    #node_name -> name of the node the pub/sub is connecting to
    #tel -> the class object created using the DataClass Types
    async def publish_NATS(self, tel):

        #Creating the vehicle data dictionary
        vehicle_data = {'speed': tel.speed, 
                        'pitch': tel.pitch, 
                        'yaw': tel.yaw, 
                        'roll': tel.roll, 
                        'altitude': tel.altitude, 
                        'batteryLife': tel.batteryLife, 
                        'lastUpdated': tel.lastUpdated, 
                        'currentPosition': str(tel.currentCoordinate)}
        
        #Turning vehicle_data into a json
        jsondata = json.dumps(vehicle_data, default=str)
        
        #Sending the data
        await self.connection.publish(self.node_name, bytes(jsondata,encoding='utf-8'))
        await self.subscriber.next_msg()
        print("Sent the following message: ")
        print(jsondata) 

    async def close_NATS(self):
        print("Closing...draining remaing messages:")
        await self.subscriber.unsubscribe()
        await self.connection.drain()
        print("Connection Closed")