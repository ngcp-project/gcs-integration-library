# Dummy GCS
#!/usr/bin/env python
import pika
import uuid
import time
import json
from Types.Commands import Commands
from Types.CommandsEnum import CommandsEnum
from Types.Geolocation import Coordinate, Polygon

class GCSRabbitMQ:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, vehicleName: str, command_type: str, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        last_call = time.time()
        message = json.dumps(data.to_dict())
        # command_name = data
        queue_name = f"{vehicleName.lower()}_command_{command_type}"

        print(f"message: {data}")
        print(f"====== queue_name here {queue_name}=====")

        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            properties=pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id),
            body=message
        )
        print(f" [x] Sent commands to {vehicleName}: \n\t {message}\n")
        while self.response is None:
            time.sleep(1)
            self.connection.process_data_events(time_limit=3)
            if time.time() - last_call > 3:
                print(f"[x] Vehicle {vehicleName} is missing [x]")
                return "Vehicle is missing"
        return str(self.response)

# if __name__ == "__main__":
gcs_rpc = GCSRabbitMQ()

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

data_eru = Commands(
    isManual=True,
    emergencyStop=False,
    target=coordinates_01,
    searchArea=search_area_list,
    keepIn=keep_in_list,
    keepOut=keep_out_list
)

command_type = CommandsEnum.MANUAL_MODE
response_eru = gcs_rpc.call("eru", command_type, data_eru)
print(f"Command is: {data_eru.isManual}")
print(f"Response from ERU: {response_eru}")

# response_mea = gcs_rpc.call("mea", data_mea)
# print(f"Response from MEA: {response_mea}")
