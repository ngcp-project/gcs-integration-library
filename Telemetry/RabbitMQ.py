import pika, sys

class TelemetryRabbitMQ:
    def __init__(self, vehicleName, rabbitMQCredentials):
        self.vehicleName = vehicleName
        self.rabbitMQCredentials = rabbitMQCredentials
        self.connection = None
        self.channel = None
        self.setup_rabbitmq()

    # Sets up the connection to rabbitMQ using the provided credentials
    def setup_rabbitmq(self):
        credentials = pika.PlainCredentials(
            self.rabbitMQCredentials['username'],
            self.rabbitMQCredentials['password']
        )
        parameters = pika.ConnectionParameters(
            'localhost',  # Use 'localhost' since RabbitMQ is running in a Docker container
            5672,  # Default RabbitMQ port inside the Docker container
            '/',
            credentials
        )
        # Create the connection using pika.BlockingConnection
        self.connection = pika.BlockingConnection(parameters)
        # Declare a queue on the channel
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.vehicleName)

    # Publishing messages to RabbitMQ. 
    def publish(self):
        try:
            if self.channel is None:
                raise Exception("Channel is not initialized.")

            message = ' '.join(sys.argv[1:])  # Concatenate command-line arguments into a single message
            self.channel.basic_publish(
                exchange='',
                routing_key=self.vehicleName,
                body=message.encode()  # Encode the message as bytes before sending
            )
        except Exception as e:
            print(f"Exception during message publishing: {e}")


    def close_connection(self):
        if self.connection:
            self.connection.close()


