# Dummy GCS
#!/usr/bin/env python
import pika
import uuid
import time
import json
from Types.Commands import Commands
from Types.Geolocation import Coordinate, Polygon

class GCSRabbitMQ(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    # Basically a callback function
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data:Commands):
        global last_call
        global flag_count
        flag_count = 0
        last_call = time.time()
        
        self.response = None
        self.corr_id = str(uuid.uuid4())
        message = json.dumps(data.to_dict())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=message)
        print(f" [x] The following commands to Vehicles: {message}")
        while self.response is None: 
            time.sleep(1)  # Delay for better visualization, remove in production
            self.connection.process_data_events(time_limit=3)
            if time.time() - last_call > 3:  # Check if 3 seconds have elapse
                print("[x] Vehicle is missing [x]")
                return "Vehicle is missing"
        return str(self.response)

gcs_rpc = GCSRabbitMQ()

print(f" [x] Start sending commands to Vehicles")
coordinates_01 = Coordinate(latitude = 35.35, longitude =  60.35)

coordinates_02 = Coordinate(latitude = 40.35, longitude =  50.35)
coordinates_03 = Coordinate(latitude = 44.35, longitude =  55.35)
search_area_coordinates = [coordinates_02, coordinates_03]

search_area_list = Polygon(coordinates =  search_area_coordinates)

data = Commands( 
    isManual=True,
    target=coordinates_01,
    searchArea=search_area_list
)

response = gcs_rpc.call(data)
print(f"Response: {response}")


    

