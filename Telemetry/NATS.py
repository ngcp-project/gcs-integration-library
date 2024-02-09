import os
import asyncio
import time
import aioconsole

import nats
from nats.errors import TimeoutError

#Initializing Telemetry Class
class TelemetryNATS:
    
    #Creating the object
    async def __init__(self):
        self.speed = None
        self.pitch = None
        self.yaw = None
        self.roll = None
        self.altitude = None
        self.batteryLife = None 
        self.lastUpdated = None #TimeStamp
        self.currentPosition = None #Coordinate Class
        self.vehicleStatus = None #Status_Exum Class
        
        #Setting up the new connection
        servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")
        #Connecting to the server
        nc = await nats.connect(servers=servers)
        #Return the new connection
        self.nc = nc
    
    #Function to run the telemetry connection.
    async def publish_NATS(self,nc,node_name,speed, pitch, yaw, roll, altitude, batteryLife, lastUpdated, currentPosition, vehicleStatus):
        print("Running")
        counter = 0
        while True:
            current_time = time.time()
            data = "{number: " + str(counter) + "}" + "\nCurrent time: " + str(current_time)
            
            await nc.publish(node_name, bytes(data,encoding='utf-8'))
            time.sleep(2)
            print("Current Iteration: " + str(counter))
            counter += 1