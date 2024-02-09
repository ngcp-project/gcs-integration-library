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
        self.nc = None    
        
    async def setup_NATS(self):
        #Setting up the new connection
        servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")
        #Connecting to the server
        self.nc = await nats.connect(servers=servers)
        
    #Function to run the telemetry connection.
    #node_name -> name of the node the pub/sub is connecting to
    #tel -> the class object created using the DataClass Types
    async def publish_NATS(self,node_name, tel):

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
        await self.nc.publish(node_name, bytes(jsondata,encoding='utf-8'))
        time.sleep(2)