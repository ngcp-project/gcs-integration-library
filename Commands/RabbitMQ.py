import json

import pika

from Types.CommandsEnum import CommandsEnum
from Types.Geolocation import Coordinate, Polygon


class CommandsRabbitMQ:
    # Initialize vehicle information
    def __init__(self, vehicleName: str, commandName, ipAddress: str):
        self.vehicleName = vehicleName.lower()
        self.commandName = commandName
        self.ipAddress = ipAddress
        self.connection = None
        self.channel = None
        self.setup_rabbitmq()

    # Setting up RabbitMQ Server for Vehicles
    def setup_rabbitmq(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.ipAddress))
        self.channel = self.connection.channel()
        queue_name = f"{self.vehicleName}_command_{self.commandName.value}"
        self.channel.queue_declare(queue=queue_name)
        print(f"queue_name in setup {queue_name}")

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

    def subscribe(self, topic: str, callback_function) -> str:
        """
        - Function to subscribe to only one topic from the given commands from GCS.
        - Calls handle_command() function to handle the single given command.
        """
        print("Enter Subscribe")
        queue_name = f"{self.vehicleName}_command_{self.commandName.value}"
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback_function, auto_ack=False)

    def subscribe_all(self, callback_function) -> str:
        """
        - Function to subscribe to all the commands given from the GCS.
        - Calls handle_all_commands() function to handle the given command.
        """
        command_types = ["manual", "emergency", "target", "searchArea", "keepIn", "keepOut"]
        for command_type in command_types:
            queue_name = f"{self.vehicleName}_commands_{command_type}"
            self.channel.queue_declare(queue=queue_name)
            self.channel.basic_consume(queue=queue_name, on_message_callback=callback_function, auto_ack=False)

    def start_consuming(self):
        self.channel.start_consuming()

    def handle_command(self, channel, method, props, body):
        """
        - Function to handle the data given from command and its topic.
        - It determines which command function to call based on given topic.
        """
        if self.channel is None:
            raise Exception("Channel is not initialized.")

        command_dict = json.loads(body)
        command_type = self.commandName.value
        response = ""

        print(f"====== Commands Types ======> {command_type}")

        print(f"====== Vehicle Name ======> {self.vehicleName.upper()}")

        match(command_type):
            case CommandsEnum.manual.value:
                self.isManual(command_dict["isManual"])
                response = f"[.] Vehicle received commands from GCS with data: {command_type} = {command_dict['isManual']}"
            case CommandsEnum.target.value:
                self.target(command_dict["target"])
                response = f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict['target']}"
            case CommandsEnum.emergency.value:
                self.emergencyStop(command_dict["emergencyStop"])
                response = (
                    f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict['emergencyStop']}"
                )
            case CommandsEnum.search.value:
                self.searchArea(command_dict["searchArea"])
                response = f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict['searchArea']}"
            case CommandsEnum.keepIn.value:
                self.keepIn(command_dict["keepIn"])
                response = f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict['keepIn']}"
            case CommandsEnum.keepOut.value:
                self.keepOut(command_dict["keepOut"])
                response = f"[.] Vehicle received commands from GCS with data:{command_type} = {command_dict['keepOut']}"

        channel.basic_publish(
            exchange="",
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=str(response),
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def close_connection(self):
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    vehicleName = "eru"
    command_name = CommandsEnum.keepIn
    ip_address = "localhost"  # Replace with the actual GCS IP address
    vehicle = CommandsRabbitMQ(vehicleName, command_name, ip_address)

    def callback(ch, method, props, body):
        vehicle.handle_command(ch, method, props, body)

    try:
        vehicle.subscribe(command_name.value, callback)
        vehicle.start_consuming()
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()
