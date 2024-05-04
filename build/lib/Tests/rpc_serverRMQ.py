# Vehicle

import pika 
import time
import json
from Types.Commands import Commands
from Types.Geolocation import Coordinate, Polygon

class CommandsRabbitMQ:
    def __init__(self, vehicleName: str):
        self.vehicleName = vehicleName.lower()
        self.connection = None
        self.channel = None
        self.setup_rabbitmq()
        
    def setup_rabbitmq(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel(0)
        self.channel.queue_declare(queue='rpc_queue')

    def isManual(self, isManual: bool):
        print(f"Manual is:{isManual}")
        
    def target(self, target: Coordinate):
        print(f"Target Coordinate is:{target}")
        
    def searchArea(self, searchArea: Polygon):
        print(f"Search Area is:{searchArea}")
        
    def subscribe_all(self, callback_function) -> str:
        print("Enter subscribe_all")
        def callback(ch, method, props, body):
            print("Enter callback")
            commands = json.loads(body)
            callback_function(ch, method, props, commands)
            self.handle_commands(commands, ch, props, method)
        
        self.channel.basic_qos(prefetch_count=1)    
        self.channel.basic_consume(queue='rpc_queue', on_message_callback=callback)
        print(" [x] Awaiting GCS RPC requests")
        self.channel.start_consuming()
            
        
    def handle_commands(self, command_dict, ch, props, method):   
        print("Enter handle_commands")
        if self.channel is None:
            raise Exception("Channel is not initialized.")
        is_manual = command_dict['isManual']
        target_latitude = command_dict['target']['latitude']
        target_longitude = command_dict['target']['longitude']
        
        search_area_coordinates = command_dict['searchArea']['coordinates']
        search_area_coordinates_list = []
        for coor_dict in search_area_coordinates:
            search_area_latitude = coor_dict['latitude']
            search_area_longitude = coor_dict['longitude']
            search_area_coordinates_list.append(Coordinate(latitude=search_area_latitude, longitude=search_area_longitude))
                    
        targetCoordinate = Coordinate(target_latitude, target_longitude)
        search_area = Polygon(coordinates=search_area_coordinates_list)
        
        self.isManual(is_manual)
        self.target(targetCoordinate)
        self.searchArea(search_area)
        
        response = {f"[.] Vehicle recieved commands from GCS with data:{command_dict}"}
        ch.basic_publish(exchange='', routing_key=props.reply_to, 
                        properties=pika.BasicProperties(correlation_id=props.correlation_id),
                        body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        last_call = time.time() 
        
    def close_connection(self):
        if self.connection:
            self.connection.close()       
            
if __name__=="__main__":
    vehicle = CommandsRabbitMQ("ERU")
    def callback(channel, method, prop, body):
        print("Callback in Main received data from GCS")
        print(body)
    try:
        vehicle.subscribe_all(callback)
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()


