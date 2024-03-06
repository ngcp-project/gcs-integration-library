import datetime
import os
import asyncio
import time
import json

import nats
from nats.errors import TimeoutError

#Initializing Telemetry Class
class TelemetryNATS:
        
    #Creating the object
    def __init__(self):      
        self.connection = None 
        self.node_name = None
        self.subscriber = None
   
    #Setting up the connection
    async def setup_NATS(self,node_name, ipv4):
        print("Attempting to connect...")

        #Setting up the new connection
        servers = os.environ.get("NATS_URL", "nats://" + ipv4 + ":4222").split(",")

        #Connecting to the server
        self.connection = await nats.connect(servers=servers,)
        self.node_name = node_name
        self.subscriber = await self.connection.subscribe(node_name) #Used to wait for the next message before sending another
        
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
                        'currentPosition': str(tel.currentCoordinate), 
                        'vehicleStatus': str(tel.vehicleStatus)}
        
        #Turning vehicle_data into a json
        jsondata = json.dumps(vehicle_data, default=str)
        
        #Sending the data
        await self.connection.publish(self.node_name, bytes(jsondata,encoding='utf-8'))
        await self.subscriber.next_msg() 