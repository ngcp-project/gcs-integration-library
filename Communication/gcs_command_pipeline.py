#!/usr/bin/env python
import json
import time
import pika
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Communication.XBee.XBee import XBee  # Import your XBee wrapper

# --- Configuration ---
RABBITMQ_HOST = 'localhost'
COMMAND_QUEUE = 'vehicle_commands'
ACK_QUEUE = 'command_acknowledgements'

# Use the appropriate serial port for the GCS XBee.
# On Windows, for example, "COM4"; on macOS, use "/dev/cu.usbserial-XXXX"
SENDER_PORT = 'COM4'
BAUD_RATE = 115200

# Mapping from vehicle ID string to a numeric code for our minimal packet.
VEHICLE_MAP = {"ERU": 0x01, "MEA": 0x02, "MRA": 0x03, "FRA": 0x04}

def publish_ack(ack_message):
    """Publish the acknowledgment message back to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=ACK_QUEUE, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=ACK_QUEUE,
        body=json.dumps(ack_message)
    )
    print("[GCS] Published ack:", ack_message)
    connection.close()

def process_command_message(ch, method, properties, body):
    """
    Process a command message received from RabbitMQ.
    Expected JSON format:
      {
          "vehicle_id": "ERU",
          "command_type": "EMERGENCY_STOP",
          "command_data": {"emergency": true}
      }
    For an emergency stop, we create a minimal 2-byte command:
      Byte 1: 0x01 (emergency stop)
      Byte 2: Vehicle code (from VEHICLE_MAP)
    """
    try:
        command_msg = json.loads(body.decode('utf-8'))
        print("[GCS] Received command from RabbitMQ:", command_msg)
    except Exception as e:
        print("[GCS] Error parsing command message:", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # For now, we only handle emergency stop.
    if command_msg.get("command_type") != "EMERGENCY_STOP":
        print("[GCS] Unsupported command type; skipping.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    vehicle_str = command_msg.get("vehicle_id", "")
    if vehicle_str not in VEHICLE_MAP:
        print(f"[GCS] Unknown vehicle_id: {vehicle_str}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Build the minimal binary command: 2 bytes.
    command_packet = bytes([0x01, VEHICLE_MAP[vehicle_str]])
    print("[GCS] Sending minimal binary command over XBee:", command_packet.hex())

    # Create and open the XBee instance.
    xbee = XBee(SENDER_PORT, BAUD_RATE)
    if not xbee.open():
        print("[GCS] Error: Could not open XBee on", SENDER_PORT)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Use the XBee wrapper to transmit the binary packet.
    xbee.transmit_data(command_packet)
    print("[GCS] Transmitted command packet via XBee.")

    # Wait for an acknowledgment (assumed to be a newline-terminated JSON string).
    start_time = time.time()
    ack_received = None
    while time.time() - start_time < 5:
        response = xbee.retrieve_data()
        if response:
            try:
                ack_received = json.loads(response.data.decode('utf-8'))
                print("[GCS] Received ack from vehicle:", ack_received)
                break
            except Exception as e:
                print("[GCS] Error parsing ack:", e)
    if ack_received is None:
        ack_received = {"vehicle_id": vehicle_str, "command": "EMERGENCY_STOP", "status": "no_ack"}
        print("[GCS] No ack received within timeout.")

    publish_ack(ack_received)
    xbee.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_rabbitmq_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=COMMAND_QUEUE, durable=True)
    channel.basic_consume(queue=COMMAND_QUEUE, on_message_callback=process_command_message)
    print("[GCS] Waiting for command messages on queue:", COMMAND_QUEUE)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[GCS] Consumer interrupted. Exiting...")
        channel.stop_consuming()
    connection.close()

if __name__ == '__main__':
    start_rabbitmq_consumer()
