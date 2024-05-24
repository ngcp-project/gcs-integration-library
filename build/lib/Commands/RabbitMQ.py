import pika 
import time
import json
from Types.Commands import Commands
from Types.CommandsEnum import CommandsEnum
from Types.Geolocation import Coordinate, Polygon
        
class CommandsRabbitMQ:
    # Initialize vehicle information
    def __init__(self, vehicleName: str, ipAddress: str = 'localhost'):
        self.vehicleName = vehicleName.lower()
        self.connection = None
        self.channel = None
        self.ipAddress = ipAddress
        self.setup_rabbitmq()
        
    # Setting up RabbitMQ Server for Vehicles    
    def setup_rabbitmq(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.ipAddress))
        self.channel = self.connection.channel()

    """
    isManual(isManual: bool)
    
    emergencyStop(emergencyStop : bool)
    
    taregt(target: Coordinate)
    
    searchArea(searchArea: Polygon)
    
    keepIn(keepIn: Polygon)
    
    keepOut(keepOut: Polygon)
    """
    def isManual(self, isManual: bool):
        print(f"Manual is: {isManual}")
    
    def emergencyStop(self, emergencyStop: bool):
        print(f"Emergency Stop is: {emergencyStop}")
        
    def target(self, target: Coordinate):
        print(f"Target Coordinate is: {target}")
        
    def searchArea(self, searchArea: Polygon):
        print(f"Search Area is: {searchArea}")
        
    def keepIn(self, keepIn: Polygon):
        print(f"Keep in Coordinate is: {keepIn}")
    
    def keepOut(self, keepOut: Polygon):
        print(f"Keep out Coordinate is: {keepOut}")
    
    """
    subscribe(self, topic: str, callback_function)
    
    -Function to subcribe to only one topic from the given commands from GCS.
    -Calls handle_command() function to handle the single given command.
    
    """
    def subscribe(self, commandName: CommandsEnum, callback_function) -> str:
        print("Enter Subscribe")
        queue_name = f"{self.vehicleName.lower()}_command_{commandName}"
        self.channel.queue_declare(queue=queue_name)
        
        def callback(ch, method, props, body):
            msg = json.loads(body)
            callback_function(json.loads(body))
            self.handle_command(msg, commandName.value, ch, props, method)
        
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        # self.channel.start_consuming()
    
    """
    subscribe_all(self, callback_function)
    
    - Function to subcribe to all the commands given from the GCS.
    -Calls handle_all_commands() function to handle the given command.
    
    """
    def subscribe_all(self, vehicleName: str, callback_function) -> str:
        command_types = ["manual", "emergency", "target", "search", "keepIn", "keepOut"]
        for command_type in command_types:
            queue_name = f"{self.vehicleName.lower()}_commands_{command_type}"
            self.channel.queue_declare(queue=queue_name)
        
        def callback(ch, vehicleName: str, method, props, body):
            commands = json.loads(body)
            callback_function(ch, method, props, commands)
            self.handle_all_commands(vehicleName, commands, ch, props, method)
        
        self.channel.basic_consume(queue='rpc_queue', on_message_callback=callback, auto_ack=False)
        self.channel.start_consuming()

    """
    handle_command(self, topic, command_dict, ch, props, method):
    
    - Function to handle the data given from command and its topic.
    - It determines which command function to call based on given topic.
    
    """
    def handle_command(self, msg, topic, ch, props, method):
        if self.channel is None:
            raise Exception("Channel is not initialized.")
        
        response = ''

        print(f"====== Commands Types ======> {topic.upper()}")
        
        print(f"====== Vehicle Name ======> {self.vehicleName.upper()}")

        # if command_type == CommandsEnum.MANUAL_MODE.value:
        #     self.isManual(command_dict["isManual"])
        #     response = {f"[.] Vehicle received commands from GCS with data: {command_type} = {command_dict["isManual"]}"}
        # elif command_type == CommandsEnum.TARGET.value:
        #     self.target(command_dict["target"])
        #     response = {f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict["target"]}"}
        # elif command_type == CommandsEnum.EMERGENCY_STOP.value:
        #     self.emergencyStop(command_dict["emergencyStop"])
        #     response = {f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict["emergencyStop"]}"}
        # elif command_type == CommandsEnum.SEARCH_AREA.value:
        #     self.searchArea(command_dict["searchArea"])
        #     response = {f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict["seachArea"]}"}
        # elif command_type == CommandsEnum.KEEP_IN.value:
        #     self.keepIn(command_dict["keepIn"])
        #     response = {f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict["keepIn"]}"}
        # elif command_type == CommandsEnum.KEEP_OUT.value:
        #     self.keepOut(command_dict["keepOut"])
        #     response = {f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict["keepOut"]}"}

        # time.sleep(4)
        
        ch.basic_publish(
            exchange='', 
            routing_key=props.reply_to, 
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=str(msg)
        )
        # Use the delivery tag from the method argument for acknowledgment
        ch.basic_ack(delivery_tag=method.delivery_tag)
        last_call = time.time() 
        
    """
    handle_all_command(self, command_dict, ch, props, method):
    
    - Function to handle the data given from command.
    - It parses the given data in json format and passes those data to 
    destined functions.
    
    """
    def handle_all_commands(self, vehicleName, command_dict, ch, props, method): 
          
        print("Enter handle_all_commands")
        print(f"====== Vehicle Name ======> {vehicleName.upper()}")
        if self.channel is None:
            raise Exception("Channel is not initialized.")
        
        command_type = command_dict.get("isManual")
            
        is_manual = command_dict['isManual']
        emergency_stop = command_dict['emergencyStop']
        target_latitude = command_dict['target']['latitude']
        target_longitude = command_dict['target']['longitude']
        
        search_area_coordinates = command_dict['searchArea']['coordinates']
        search_area_coordinates_list = []
        for coor_dict in search_area_coordinates:
            search_area_latitude = coor_dict['latitude']
            search_area_longitude = coor_dict['longitude']
            search_area_coordinates_list.append(Coordinate(latitude=search_area_latitude, longitude=search_area_longitude))
        
        keep_in_coordinates = command_dict['keepIn']['coordinates']
        keep_in_coordinates_list = []
        for coor_dict in keep_in_coordinates:
            keep_in_latitude = coor_dict['latitude']
            keep_in_longitude = coor_dict['longitude']
            keep_in_coordinates_list.append(Coordinate(latitude=keep_in_latitude, longitude=keep_in_longitude))
        
        keep_out_coordinates = command_dict['keepOut']['coordinates']
        keep_out_coordinates_list = []
        for coor_dict in keep_out_coordinates:
            keep_out_latitude = coor_dict['latitude']
            keep_out_longitude = coor_dict['longitude']
            keep_out_coordinates_list.append(Coordinate(latitude=keep_out_latitude, longitude=keep_out_longitude))
                    
        targetCoordinate = Coordinate(target_latitude, target_longitude)
        search_area = Polygon(coordinates=search_area_coordinates_list)
        keep_in = Polygon(coordinates=keep_in_coordinates_list)
        keep_out = Polygon(coordinates=keep_out_coordinates_list)
        
        
        self.isManual(is_manual)
        self.emergencyStop(emergency_stop)
        self.target(targetCoordinate)
        self.searchArea(search_area)
        self.keepIn(keep_in)
        self.keepOut(keep_out)
        
        # time.sleep(4)
        response = {f"[.] Vehicle received commands from GCS with data:\n\t{command_dict}\n"}
        ch.basic_publish(exchange='', routing_key=props.reply_to, 
                        properties=pika.BasicProperties(correlation_id=props.correlation_id),
                        body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        last_call = time.time() 
    
    def start_connection(self):
        self.channel.start_consuming()
     
    def close_connection(self):
        if self.connection:
            self.connection.close()       
            
if __name__=="__main__":
    
    # vehicleName = input("Enter vehicle name: ").strip()
    vehicleName = "eru"
    # command_name = CommandsEnum.MANUAL_MODE
    command_name = CommandsEnum.KEEP_IN
    vehicle = CommandsRabbitMQ(vehicleName, command_name)
    
    def callback(channel, method, prop, body):
        pass
    try:
        vehicle.subscribe(command_name, vehicleName, CommandsEnum.KEEP_IN.value, callback)
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()
