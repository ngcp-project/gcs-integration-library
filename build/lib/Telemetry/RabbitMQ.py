# Vehicles

import pika, sys, json
from Types.Telemetry import Telemetry
from Types.Geolocation import Coordinate
from datetime import datetime
import time
class TelemetryRabbitMQ:
    def __init__(self, vehicleName: str,  hostname: str):
        self.vehicleName = vehicleName.lower()
        self.connection = None
        self.channel = None
        self.setup_rabbitmq(hostname)

    # Sets up the connection to rabbitMQ using the provided credentials
    def setup_rabbitmq(self,hostname):
        # parameters = pika.ConnectionParameters(
        #     'localhost'  # Use 'localhost' since RabbitMQ is running in a Docker container
        # )
        # Create the connection using pika.BlockingConnection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            hostname))
        # Declare a queue on the channel
        self.channel = self.connection.channel()
        #name of the queue is set to vehicle name
        self.channel.queue_declare(queue=f"telemetry_{self.vehicleName}")
   # telemetry = TelemetryRabbitMQ(vehicleName = "ERU") 
    # 
    # Publishing messages to RabbitMQ. 
    def publish(self, data: Telemetry): #(sel, data =(as in) telemetry data)
        if self.channel is None:
            raise Exception("Channel is not initialized.")
        
        exchange_name = self.vehicleName    
        # self.channel.exchange_declare(exchange='', exchange_type='topic')
        # # Convert objects into json strings(not all are convertible, may
        # need to create a dict of data before serializing to json)
        message = json.dumps(data.to_dict())
        self.channel.basic_publish(
            # need to change exchange type to 'topic', not default
            exchange='',
            routing_key=f"telemetry_{self.vehicleName}",
            #need to change this 
            #want to do something like: 
            # telemetry.publish(data) where data is from Telemtry types file. 
            body=message  # Encode the message as bytes before sending. 
            # might not need to encode the message. 
        )
        print(f"Published message for {self.vehicleName}: {message}")
        # except Exception as e:
        #     print(f"Exception during message publishing: {e}")


    def close_connection(self):
        if self.connection:
            self.connection.close()
    
if __name__ == "__main__":
    # vehicle_name = input("Enter vehicle name: ")
    telemetry = TelemetryRabbitMQ("eru", "192.168.0.101")
    current_coordinate = Coordinate(latitude=37.7749, longitude=-122.4194)
    vehicleSearch_coordinate = Coordinate(latitude=1.0, longitude=2.0)
    while True:
        data = Telemetry(
            localIP="12.12.12.12",
            pitch=10.5,
            yaw=20.3,
            roll=5.8,
            speed=45.2,
            altitude=1000.0,
            batteryLife=80.5,
            currentCoordinate=current_coordinate,
            lastUpdated=datetime.now(),
            fireFound=False,
            vehicleSearch=vehicleSearch_coordinate
        )
        telemetry.publish(data)
        time.sleep(10)

