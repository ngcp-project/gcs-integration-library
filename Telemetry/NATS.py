import datetime
import os
import asyncio
import time
import aioconsole
import json

import nats
from nats.errors import TimeoutError

#Initializing Telemetry Class
class TelemetryNATS:
        
    #Creating the object
    async def __init__(self):      
        self.nc = None    
        
    async def setup_NATS(self):
        #Setting up the new connection
        servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")
        #Connecting to the server
        self.nc = await nats.connect(servers=servers)
        
    #Function to run the telemetry connection.
    async def publish_NATS(self,node_name,speed, pitch, yaw, roll, altitude, batteryLife, currentPosition, vehicleStatus):

        #Creating the vehicle data dictionary
        vehicle_data = {'speed': speed, 
                        'pitch': pitch, 
                        'yaw': yaw, 
                        'roll': roll, 
                        'altitude': altitude, 
                        'batteryLife': batteryLife, 
                        'lastUpdated': time.time(), 
                        'currentPosition': currentPosition, 
                        'vehicleStatus': vehicleStatus}
        
        #Turning vehicle_data into a json
        jsondata = json.dumps(vehicle_data)
        print
        #Sending the data
        await self.nc.publish(node_name, bytes(jsondata,encoding='utf-8'))
        time.sleep(2)