import pika
import json

class CommandRabbitMQConsumer:
    """
    RabbitMQ consumer that listens to 'vehicle_commands' queue and forwards
    parsed JSON messages to a provided handler function in GCS.
    """
    def __init__(self, queue_name='vehicle_commands', on_command=None):
        """
        Args:
            queue_name (str): Name of the RabbitMQ queue to subscribe to.
            on_command (callable): Handler function to call with the command JSON.
        """
        self.queue = queue_name
        self.on_command = on_command

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def start(self):
        """Start consuming from the RabbitMQ queue."""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue, on_message_callback=self._on_message)
        print(f"📥 [RabbitMQ] Listening on '{self.queue}' queue...")
        self.channel.start_consuming()

    def _on_message(self, ch, method, props, body):
        """Internal callback to handle new messages."""
        try:
            msg = json.loads(body)
            if self.on_command:
                self.on_command(msg)
        except Exception as e:
            print(f"[!] Error processing RabbitMQ message: {e}")
        finally:
            ch.basic_ack(method.delivery_tag)

    def stop(self):
        if self.connection:
            self.connection.close()