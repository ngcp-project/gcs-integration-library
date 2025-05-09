# Vehicles

import pika, sys, json
from Types.Telemetry import Telemetry, RequestCoordinates
from Types.Geolocation import Coordinate
from Types.Communication import Message
from datetime import datetime
import time
class TelemetryRabbitMQ:
    def __init__(self, vehicleName: str,  hostname: str):
        self.vehicleName = vehicleName.lower()
        self.connection = None
        self.channel = None
        self.setup_rabbitmq(hostname)

    # Sets up the connection to rabbitMQ using the provided credentials
    def setup_rabbitmq(self, hostname):
        credentials = pika.PlainCredentials("admin", "admin")  # use your actual RabbitMQ username/password
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=hostname,
            credentials=credentials
        ))
        self.channel = self.connection.channel()
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
        if hasattr(data, 'to_dict'):
            message = json.dumps(data.to_dict(), indent=4, default=str)  # For objects with to_dict
        else:
            message = json.dumps(data, indent=4)
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
        print(f"Published message for {self.vehicleName.capitalize()}: {message}")
        # except Exception as e:
        #     print(f"Exception during message publishing: {e}")


    def close_connection(self):
        if self.connection:
            self.connection.close()
    
if __name__ == "__main__":
    vehicle_list = {"eru", "mra", "mea"}
    i = 0
        # current_coordinate = Coordinate(latitude=37.7749, longitude=-122.4194)
        # vehicleSearch_coordinate = Coordinate(latitude=1.0, longitude=2.0)
        # request_location = Coordinate(latitude=45.8484, longitude=100.4194)
        # request_coordinates = RequestCoordinates(messageFlag=1, requestLocation=request_location)
    while True:
        tel_data = {
            "pitch":10.5 + i,
            "yaw":20.3 + i,
            "roll":5.8 + i + 2,
            "speed":45.2 + i,
            "alt":1000.0+ i,
            "battery_life":0.85,
            "current_latitude": 12.222 + i + 20,
            "current_longitude":33.22 + i + 30,
            "lastUpdated":datetime.now().isoformat(),
            "vehicle_status": 1 + i,
            "patient_status": 2,
            "message_flag": 1+ i,
            "message_lat":22.22 + i,
            "message_lon":656.22 + i
        }
        i += 1
        for vehicle in vehicle_list:
            telemetry = TelemetryRabbitMQ(f"{vehicle}", "localhost")
            # transmit_data = Message(vehId=1, type=1, telemetryData=tel_data)
            telemetry.publish(tel_data)
        time.sleep(1)

