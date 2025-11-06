import sys
import threading
import time
import json
import os
from datetime import datetime

# RabbitMQ client
import pika

# XBee infrastructure
sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')
from Communication.XBee import XBee
from Communication.Frames.x81 import x81
from Logger.Logger import Logger

# Constants
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

# Vehicles map
VEHICLES = {
    "MRA": {"MAC": "0013A200424353F7", "short": "0002"},
    "ERU": {"MAC": "NaN",             "short": "0003"},
    "MEA": {"MAC": "0013A2004243672F", "short": "0004"},
}

# Command names
COMMANDS = {
    1: "KEEP_IN_ZONE",
    2: "EMERGENCY_STOP",
    3: "MOVE_TO_COORD",
    4: "RETURN_HOME",
}

# RabbitMQ setup
def setup_rabbitmq():
    amqp_url = os.getenv('AMQP_ADDR', 'amqp://admin:admin@localhost:5672/%2f')
    params = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # Declare telemetry and commands queues
    channel.queue_declare(queue='vehicle_telemetry', durable=True)
    channel.queue_declare(queue='vehicle_commands', durable=True)
    return connection, channel

# Initialize RabbitMQ
rabbit_conn, rabbit_ch = setup_rabbitmq()

# Logger & XBee setup
logger = Logger(log_to_console=False)
gcs_xbee = XBee(port="COM3", baudrate=115200, logger=logger)
gcs_xbee.open()

# Publish telemetry to RabbitMQ and log locally
def send_telemetry():
    while True:
        frame: x81 = gcs_xbee.retrieve_data()
        if frame:
            body = frame.data
            src = frame.source_address.hex().upper().zfill(4)
            if frame.data:
                tag = ord(body[0])
                payload = body[1:]
                if tag == TAG_TELEMETRY:
                    vehicle = next((n for n,i in VEHICLES.items() if i['short']==src), 'UNKNOWN')
                    timestamp = datetime.now().isoformat()
                    telemetry = {
                        'vehicle_id': vehicle,
                        'data': payload,
                        'rssi': frame.rssi,
                        'timestamp': timestamp
                    }
                    # Publish to RabbitMQ
                    rabbit_ch.basic_publish(
                        exchange='', routing_key='vehicle_telemetry',
                        body=json.dumps(telemetry),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    # Local log
                    with open('gcs_telemetry_log.txt','a') as f:
                        f.write(f"[{timestamp}] {vehicle} | {payload}\n")
        time.sleep(0.05)

# Consume commands from RabbitMQ and forward over XBee
def listen_for_commands():
    def callback(ch, method, properties, body):
        try:
            msg = json.loads(body)
            vid = msg.get('vehicle_id')
            cmd_id = int(msg.get('value', msg.get('command_id', 0)))
        except Exception:
            ch.basic_ack(method.delivery_tag)
            return
        info = VEHICLES.get(vid)
        if not info or info['MAC']=='NaN':
            ch.basic_ack(method.delivery_tag)
            return
        # Send over XBee
        payload = chr(TAG_COMMAND)+str(cmd_id)
        gcs_xbee.transmit_data(payload, address=info['MAC'], retrieveStatus=True)
        print(f"Forwarded cmd {cmd_id} to {vid}")
        ch.basic_ack(method.delivery_tag)

    rabbit_ch.basic_qos(prefetch_count=1)
    rabbit_ch.basic_consume(queue='vehicle_commands', on_message_callback=callback)
    rabbit_ch.start_consuming()

# Entrypoint
def main():
    t1 = threading.Thread(target=send_telemetry, daemon=True)
    t2 = threading.Thread(target=listen_for_commands, daemon=True)
    t1.start()
    t2.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        rabbit_conn.close()
        gcs_xbee.close()

if __name__ == '__main__':
    main()
