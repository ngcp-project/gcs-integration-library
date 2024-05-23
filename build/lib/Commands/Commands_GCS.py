# Dummy GCS
#!/usr/bin/env python
import pika
import uuid
import time
import json
from Types.Commands import Commands
from Types.CommandsEnum import CommandsEnum
from Types.Geolocation import Coordinate, Polygon

vehicles_list = ['eru', 'mra', 'fra', 'mea']

class GCSRabbitMQ:
    def __init__(self, vehicleName, ipAddress):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=ipAddress))
        self.channel = self.connection.channel()
        self.vehicleName = vehicleName
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, command_type: str, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        last_call = time.time()
        message = json.dumps(data.to_dict())
        queue_name = f"{self.vehicleName}_command_{command_type.value}"

        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            properties=pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id),
            body=message
        )
        print(f" [x] Sent commands to {self.vehicleName}")
        while self.response is None:
            self.connection.process_data_events(time_limit=1)
            if time.time() - last_call > 3:
                print(f"[x] Vehicle {self.vehicleName} is missing [x]")
                return "Vehicle is missing"
        return str(self.response)


print(" [x] Start sending commands to Vehicles")
coordinates_01 = Coordinate(latitude=35.35, longitude=60.35)
coordinates_02 = Coordinate(latitude=40.35, longitude=50.35)
coordinates_03 = Coordinate(latitude=44.35, longitude=55.35)
search_area_coordinates = [coordinates_02, coordinates_03]
search_area_list = Polygon(coordinates=search_area_coordinates)

coordinates_04 = Coordinate(latitude=40.35, longitude=50.35)
coordinates_05 = Coordinate(latitude=44.35, longitude=55.35)
keep_in_coordinates = [coordinates_04, coordinates_05]
keep_in_list = Polygon(coordinates=keep_in_coordinates)

coordinates_06 = Coordinate(latitude=40.35, longitude=50.35)
coordinates_07 = Coordinate(latitude=44.35, longitude=55.35)
keep_out_coordinates = [coordinates_06, coordinates_07]
keep_out_list = Polygon(coordinates=keep_out_coordinates)

data = Commands(
    isManual=True,
    emergencyStop=False,
    target=coordinates_01,
    searchArea=search_area_list,
    keepIn=keep_in_list,
    keepOut=keep_out_list
)

command_type = CommandsEnum.keepIn
ip_address = "192.168.1.100"  # Replace with the actual GCS IP address

### For Keep_In, Keep_Out Zone:
if command_type == CommandsEnum.keepIn:
    for vehicle_name in vehicles_list:
        gcs_rpc_vehicle = GCSRabbitMQ(vehicle_name, ip_address)
        response = gcs_rpc_vehicle.call(command_type, data)
        print(f"\nResponse from {vehicle_name.upper()}: {response}")
