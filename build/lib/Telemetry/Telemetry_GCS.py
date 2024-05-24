# GCS

import pika, sys, json
# from Types.Telemetry import Status, Telemetry
# from Types.Geolocation import Coordinate
from datetime import datetime
import time

class TelemetrySubscriber:
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

        binding_key = 'telemetry'
        # if not binding_keys:
        #     sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
        #     sys.exit(1)
        self.channel.queue_bind(exchange=self.vehicleName, queue=self.queue_name, routing_key=self.binding_key)

        print(f" [*] Waiting for telemetry data for {self.vehicleName}. To exit press CTRL+C")

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)

    def callback(self, ch, method, properties, body):
        telemetry_data = body
        print(f"Received telemetry data for {self.vehicleName}: {telemetry_data}")

    def start_consuming(self):
        self.channel.start_consuming()
        
    def close_connection(self):
        if self.connection:
            self.connection.close()

# Example usage:
if __name__ == "__main__":
    # Replace 'ERU' with your vehicle name and 'telemetry.sensor1' with your desired binding key
    subscriber = TelemetrySubscriber(vehicleName="ERU", binding_key="telemetry")

    try:
        subscriber.start_consuming()
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        subscriber.close_connection()
