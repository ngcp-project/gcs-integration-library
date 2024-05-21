# Vehicle

import pika 
import time
import json
from Types.Commands import Commands
from Types.CommandsEnum import CommandsEnum
from Types.Geolocation import Coordinate, Polygon
        
class CommandsRabbitMQ:
    # Initialize vehicle information
    def __init__(self, vehicleName: str):
        self.vehicleName = vehicleName.lower()
        self.connection = None
        self.channel = None
        self.setup_rabbitmq()
        
    # Setting up RabbitMQ Server for Vehicles    
    def setup_rabbitmq(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel(0)
        self.channel.queue_declare(queue='rpc_queue')

    """
    isManual(isManual: bool)
    
    taregt(target: Coordinate)
    
    searchArea(searchArea: Polygon)
    """
    def isManual(self, isManual: bool):
        print(f"Manual is: {isManual}")
        
    def target(self, target: Coordinate):
        print(f"Target Coordinate is: {target}")
        
    def searchArea(self, searchArea: Polygon):
        print(f"Search Area is: {searchArea}")
    
    """
    subscribe(self, topic: str, callback_function)
    
    -Function to subcribe to only one topic from the given commands from GCS.
    -Calls handle_command() function to handle the single given command.
    
    """
    def subscribe(self, topic: str, callback_function) -> str:
        def callback(ch, method, props, body):
            commands = json.loads(body)
            callback_function(ch, method, props, commands)
            self.handle_command(topic, commands, ch, props, method)
        self.channel.basic_consume(queue='rpc_queue', on_message_callback=callback, auto_ack=False)
        self.channel.start_consuming()
    
    """
    subscribe_all(self, callback_function)
    
    - Function to subcribe to all the commands given from the GCS.
    -Calls handle_all_commands() function to handle the given command.
    
    """
    def subscribe_all(self, callback_function) -> str:
        def callback(ch, method, props, body):
            commands = json.loads(body)
            callback_function(ch, method, props, commands)
            self.handle_all_commands(commands, ch, props, method)
        self.channel.basic_consume(queue='rpc_queue', on_message_callback=callback, auto_ack=False)
        self.channel.start_consuming()

    """
    handle_command(self, topic, command_dict, ch, props, method):
    
    - Function to handle the data given from command and its topic.
    - It determines which command function to call based on given topic.
    
    """
    def handle_command(self, topic, command_dict, ch, props, method):
        if self.channel is None:
            raise Exception("Channel is not initialized.")
        
        command_type = topic
        print(f"====== Commands Types ======> {command_type.upper()}")

        if command_type == CommandsEnum.MANUAL_MODE.value:
            self.isManual(command_dict["isManual"])
        elif command_type == CommandsEnum.TARGET.value:
            self.target(command_dict["target"])
        elif command_type == CommandsEnum.SEARCH_AREA.value:
            self.searchArea(command_dict["searchArea"])
            
        # time.sleep(4)
        response = {f"[.] Vehicle received commands from GCS with data:{command_dict}"}
        ch.basic_publish(exchange='', routing_key=props.reply_to, 
                        properties=pika.BasicProperties(correlation_id=props.correlation_id),
                        body=str(response))
        # Use the delivery tag from the method argument for acknowledgment
        ch.basic_ack(delivery_tag=method.delivery_tag)
        last_call = time.time() 
        
    """
    handle_all_command(self, command_dict, ch, props, method):
    
    - Function to handle the data given from command.
    - It parses the given data in json format and passes those data to 
    destined functions.
    
    """
    def handle_all_commands(self, command_dict, ch, props, method): 
          
        print("Enter handle_all_commands")
        if self.channel is None:
            raise Exception("Channel is not initialized.")
        
        command_type = command_dict.get("isManual")
            
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
        
        # time.sleep(4)
        response = {f"[.] Vehicle received commands from GCS with data:\n\t{command_dict}\n"}
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
        pass
    try:
        vehicle.subscribe(CommandsEnum.TARGET.value, callback)
        # vehicle.subscribe_all(callback)
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()


