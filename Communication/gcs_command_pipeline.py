#!/usr/bin/env python
import json
import time
import pika
import serial
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Commands.CommandsStruct import Commands  # Import your shared Commands class

# --- Configuration ---
RABBITMQ_HOST = 'localhost'
COMMAND_QUEUE = 'vehicle_commands'
ACK_QUEUE = 'command_acknowledgements'

# Serial port for the XBee on the GCS side.
SERIAL_PORT = '/dev/cu.usbserial-D30DWZL4'  # Adjust as needed
BAUD_RATE = 115200

# Expected size of the binary command packet (as defined in our Commands struct)
EXPECTED_COMMAND_SIZE = 85

# Mapping of vehicle string IDs to numeric codes
VEHICLE_MAP = {"ERU": 0x01, "MEA": 0x02, "MRA": 0x03, "FRA": 0x04}

# Open serial connection for XBee
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"[GCS] Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print("[GCS] Error opening serial port:", e)
    exit(1)

def publish_ack(ack_message):
    """Publish the acknowledgement message back to RabbitMQ."""
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
    Process incoming command message from RabbitMQ.
    Expected JSON format:
      {
          "vehicle_id": "ERU",
          "command_type": "EMERGENCY_STOP",
          "command_data": {"emergency": true}
      }
    For an emergency stop command, we construct a Commands object.
    """
    try:
        command_msg = json.loads(body.decode('utf-8'))
        print("[GCS] Received command from RabbitMQ:", command_msg)
    except Exception as e:
        print("[GCS] Error parsing command message:", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Only handle emergency stop commands for now.
    if command_msg.get("command_type") != "EMERGENCY_STOP":
        print("[GCS] Unsupported command type; skipping.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    vehicle_str = command_msg.get("vehicle_id", "")
    if vehicle_str not in VEHICLE_MAP:
        print(f"[GCS] Unknown vehicle_id: {vehicle_str}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Create a Commands object. For an emergency stop, we set emergency_stop True and default others.
    cmd_obj = Commands(
        vehicle_id=VEHICLE_MAP[vehicle_str],
        emergency_stop=True,
        autonomous_enabled=False,
        mission_lat=0.0,
        mission_lon=0.0,
        keep_in_flag=0,
        keep_in_coord1=(0.0, 0.0),
        keep_in_coord2=(0.0, 0.0),
        keep_out_flag=0,
        keep_out_coord1=(0.0, 0.0),
        keep_out_coord2=(0.0, 0.0)
    )
    binary_packet = cmd_obj.encode()
    print("[GCS] Sending binary command over XBee:", binary_packet.hex())
    try:
        ser.write(binary_packet)
    except Exception as e:
        print("[GCS] Error sending command over serial:", e)
    
    # Wait for an acknowledgment from the vehicle (assumed to be a newline-terminated JSON string)
    start_time = time.time()
    ack_received = None
    while time.time() - start_time < 5:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    ack_received = json.loads(line)
                    print("[GCS] Received ack from vehicle:", ack_received)
                    break
                except Exception as e:
                    print("[GCS] Error parsing ack:", e)
    if ack_received is None:
        ack_received = {"vehicle_id": vehicle_str, "status": "no_ack", "command": "EMERGENCY_STOP"}
        print("[GCS] No ack received within timeout.")

    publish_ack(ack_received)
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
