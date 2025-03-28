#!/usr/bin/env python
import json
import time
import pika
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Communication.XBee import XBee  # Import your XBee wrapper

# --- Configuration ---
RABBITMQ_HOST = 'localhost'
COMMAND_QUEUE = 'vehicle_commands'
ACK_QUEUE = 'command_acknowledgements'

# Use the appropriate serial port for the GCS XBee.
# On Windows, for example, "COM4"; on macOS, use "/dev/cu.usbserial-XXXX"
SENDER_PORT = '/dev/cu.usbserial-D30DWZL4'
BAUD_RATE = 115200

# Mapping from vehicle string IDs to numeric codes.
VEHICLE_MAP = {"ERU": 0x01, "MEA": 0x02, "MRA": 0x03, "FRA": 0x04}

# This GCS instance is dedicated to vehicle "ERU".
LOCAL_VEHICLE_ID = "ERU"

def publish_ack(ack_message):
    """Publish the acknowledgment message back to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=ACK_QUEUE, durable=True)
    channel.basic_publish(exchange='',
                          routing_key=ACK_QUEUE,
                          body=json.dumps(ack_message))
    print("[GCS] Published ack:", ack_message)
    connection.close()

def process_command_message(ch, method, properties, body):
    """
    Process a command message from RabbitMQ.
    Expected JSON format:
      {
          "vehicle_id": "ERU",
          "command_type": "EMERGENCY_STOP",
          "command_data": {"emergency": true}
      }
    If the command's vehicle_id does not match LOCAL_VEHICLE_ID, then do not send the command.
    """
    try:
        command_msg = json.loads(body.decode('utf-8'))
        print("[GCS] Received command from RabbitMQ:", command_msg)
    except Exception as e:
        print("[GCS] Error parsing command message:", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Only process emergency stop commands.
    if command_msg.get("command_type") != "EMERGENCY_STOP":
        print("[GCS] Unsupported command type; skipping.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    vehicle_str = command_msg.get("vehicle_id", "")
    if vehicle_str != LOCAL_VEHICLE_ID:
        print(f"[GCS] Command for {vehicle_str} ignored by this instance (assigned to {LOCAL_VEHICLE_ID}).")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Build minimal binary command packet: [0x01, vehicle_code]
    command_packet = bytes([0x01, VEHICLE_MAP[vehicle_str]])
    print("[GCS] Sending minimal binary command over XBee:", command_packet.hex())

    xbee = XBee(SENDER_PORT, BAUD_RATE)
    if not xbee.open():
        print("[GCS] Error: Could not open XBee on", SENDER_PORT)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Transmit the command packet.
    xbee.transmit_data(command_packet)
    print("[GCS] Transmitted command packet via XBee.")

    # Wait for an acknowledgment (assumed to be a newline-terminated JSON string).
    start_time = time.time()
    ack_received = None
    while time.time() - start_time < 5:
        response = xbee.retrieve_data()
        if response is None:
            continue
        # Process only received data frames (frame type 0x81).
        if not hasattr(response, 'frame_type') or response.frame_type != 0x81:
            continue
        try:
            # The payload may now be either raw bytes or a JSON string.
            if isinstance(response.data, bytes) and response.data and response.data[0] == 0x7B:
                # Looks like JSON.
                ack_received = json.loads(response.data.decode('utf-8'))
            elif isinstance(response.data, bytes) and len(response.data) < 10:
                # It's a raw command; unlikely to be an ack.
                pass
            else:
                # Otherwise, try telemetry decode (should not happen for ack).
                ack_received = None
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
