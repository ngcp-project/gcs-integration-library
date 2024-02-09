import pika, sys, json

class TelemetryRabbitMQ:
    def __init__(self, vehicleName):
        self.vehicleName = vehicleName
        self.connection = None
        self.channel = None
        self.setup_rabbitmq()

    # Sets up the connection to rabbitMQ using the provided credentials
    def setup_rabbitmq(self):
        # parameters = pika.ConnectionParameters(
        #     'localhost'  # Use 'localhost' since RabbitMQ is running in a Docker container
        # )
        # Create the connection using pika.BlockingConnection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            'localhost'))
        # Declare a queue on the channel
        self.channel = self.connection.channel()
        #name of the queue is set to vehicle name
        self.channel.queue_declare(queue=self.vehicleName)
   # telemetry = TelemetryRabbitMQ(vehicleName = "ERU") 
    # 
    # Publishing messages to RabbitMQ. 
    def publish(self, data): #(sel, data =(as in) telemetry data)
        if self.channel is None:
            raise Exception("Channel is not initialized.")
        
        exchange_name = self.vehicleName    
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        
        # Convert objects into json strings(not all are convertible, may
        # need to create a dict of data before serializing to json)
        message = json.dumps(data)
        self.channel.basic_publish(
            # need to change exchange type to 'topic', not default
            exchange='',
            routing_key='',
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

