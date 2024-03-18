import pika, json
from Types.Telemetry import Telemetry


class TelemetryRabbitMQ:
    def __init__(self, vehicleName: str, hostname: str):
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
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(hostname))
        # Declare a queue on the channel
        self.channel = self.connection.channel()
        #name of the queue is set to vehicle name
        self.channel.queue_declare(queue=f"telemetry_{self.vehicleName}")
   # telemetry = TelemetryRabbitMQ(vehicleName = "ERU") 
    # 
    # Publishing messages to RabbitMQ. 
    def publish(self, data: Telemetry): #(sel, data =(as in) telemetry data)
        if self.channel is None:
            raise Exception("RabbitMQ telemetry channel is not initialized!")
        
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
        if self.connection: self.connection.close()

