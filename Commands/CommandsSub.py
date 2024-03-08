from dataclasses import dataclass
from Types.Commands import Commands
import pika

class CommandsRabbitMQ:
    def __init__(self, vehicleName, binding_key):
        self.vehicleName = vehicleName
        self.binding_key = binding_key
        self.connection = None
        self.channel = None
        self.setup_rabbitmq()

    def setup_rabbitmq(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.vehicleName, exchange_type='topic')
        
        result = self.channel.queue_declare('', exclusive=True)
        self.queue_name = result.method.queue

        binding_key = 'commands'
        # # if not binding_keys:
        #     sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
        #     sys.exit(1)
        self.channel.queue_bind(exchange=self.vehicleName, queue=self.queue_name, routing_key=self.binding_key)

        print(f" [*] Waiting for commands for {self.vehicleName}. To exit press CTRL+C")

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
    
    def callback(self, channel, method, properties, body):
        # Insert callback code here
        commands_data = body
        print(f"Received commands for {self.vehicleName}: {commands_data}")
    

    # A method that allows the vehicle to subscribe to one specific function only. 
    def subscribe(self, topic, callback_function=callback):
        if self.channel is None:
            raise Exception("Channel is not initialized.")

        self.channel.queue_declare(queue=topic)
        self.channel.queue_bind(exchange=self.vehicleName, queue=topic)

        self.channel.basic_consume(
            queue=topic,
            on_message_callback=callback_function,
            auto_ack=True
        )

        print(f"[*] Waiting for messages on {topic}. To exit press CTRL+C")
        self.channel.start_consuming()

    # A method that allows the vehicle to subscribe to one queue 
    # that deals with all commands
    def subscribe_all(self, callback_function):
        try:
            if self.channel is None:
                raise Exception("Channel is not initialized.")

            result = self.channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue

            self.channel.queue_bind(exchange=self.vehicleName, queue=queue_name, routing_key=binding_key)

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback_function,
                auto_ack=True
            )

            print(f"[*] Waiting for messages on {queue_name}. To exit press CTRL+C")

            self.channel.start_consuming()
        except Exception as e:
            print(f"Exception during subscription: {e}")
            
    def close_connection(self):
        if self.connection:
            self.connection.close()
