import pika
import json
from datetime import datetime

class TelemetryRabbitMQ:
    def __init__(self, vehicleName: str, hostname: str):
        self.vehicleName = vehicleName.lower()
        self.connection = None
        self.channel = None
        self.setup_rabbitmq(hostname)

    def setup_rabbitmq(self, hostname):
        credentials = pika.PlainCredentials("admin", "admin")  # TODO: replace with env vars
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=hostname,
            credentials=credentials
        ))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=f"telemetry_{self.vehicleName}")
        self.channel.queue_declare(queue=f"rssi_{self.vehicleName}")

    def publish(self, data):
        if self.channel is None:
            raise Exception("RabbitMQ channel not initialized.")
        
        try:
            if hasattr(data, 'to_dict'):
                message = json.dumps(data.to_dict(), indent=4, default=str)
            else:
                message = json.dumps(data, indent=4)

            self.channel.basic_publish(
                exchange='',
                routing_key=f"telemetry_{self.vehicleName}",
                body=message
            )
            print(f"✅ Published telemetry for {self.vehicleName.upper()}")
        except Exception as e:
            print(f"[!] Failed to publish telemetry: {e}")

    def publish_rssi(self, rssi_value: int):
        if self.channel is None:
            raise Exception("RabbitMQ channel not initialized.")

        try:
            rssi_data = {
                "vehicle": self.vehicleName,
                "rssi": rssi_value,
                "timestamp": datetime.now().isoformat()
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=f"rssi_{self.vehicleName}",
                body=json.dumps(rssi_data)
            )
            print(f"✅ Published RSSI for {self.vehicleName.upper()}: {rssi_value} dBm")
        except Exception as e:
            print(f"[!] Failed to publish RSSI: {e}")

    def close_connection(self):
        if self.connection:
            self.connection.close()
