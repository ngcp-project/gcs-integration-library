from dataclasses import dataclass
import pika

class CommandsRabbitMQ:
    def __init__(self, vehicleName, rabbitMQCredentials):
        self.vehicleName = vehicleName
        self.rabbitMQCredentials = rabbitMQCredentials
        self.connection = None
        self.channel = None
        self.setup_rabbitmq()

    def setup_rabbitmq(self):
        try:
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
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
        except Exception as e:
            print(f"Exception during RabbitMQ setup: {e}")

    def subscribe_all(self, callback_function):
        try:
            if self.channel is None:
                raise Exception("Channel is not initialized.")

            result = self.channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue

            self.channel.queue_bind(exchange='commands_exchange', queue=queue_name)

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback_function,
                auto_ack=True
            )

            print(f"[*] Waiting for messages on {queue_name}. To exit press CTRL+C")

            self.channel.start_consuming()
        except Exception as e:
            print(f"Exception during subscription: {e}")

    def subscribe(self, topic, callback_function):
        try:
            if self.channel is None:
                raise Exception("Channel is not initialized.")

            self.channel.queue_declare(queue=topic)
            self.channel.queue_bind(exchange='commands_exchange', queue=topic)

            self.channel.basic_consume(
                queue=topic,
                on_message_callback=callback_function,
                auto_ack=True
            )

            print(f"[*] Waiting for messages on {topic}. To exit press CTRL+C")

            self.channel.start_consuming()
        except Exception as e:
            print(f"Exception during subscription to {topic}: {e}")

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"Exception while closing connection: {e}")
