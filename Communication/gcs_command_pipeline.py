#!/usr/bin/env python
import json
import time
import pika
import serial

# --- Configuration ---
RABBITMQ_HOST = 'localhost'
COMMAND_QUEUE = 'vehicle_commands'
ACK_QUEUE = 'command_acknowledgements'

# Serial port for the XBee on the GCS side.
SERIAL_PORT = '/dev/cu.usbserial-D30DWZL4'
BAUD_RATE = 115200

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
    channel.basic_publish(exchange='',
                          routing_key=ACK_QUEUE,
                          body=json.dumps(ack_message))
    print("[GCS] Published ack:", ack_message)
    connection.close()

def process_command_message(ch, method, properties, body):
    """
    Process incoming command message from RabbitMQ.
    Expected format:
      {
          "vehicle_id": "ERU",
          "command_type": "EMERGENCY_STOP",
          "command_data": {"emergency": true}
      }
    """
    try:
        command_msg = json.loads(body.decode('utf-8'))
        print("[GCS] Received command from RabbitMQ:", command_msg)
    except Exception as e:
        print("[GCS] Error parsing command message:", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    outgoing_command = json.dumps(command_msg)
    print("[GCS] Sending command over XBee:", outgoing_command)
    try:
        ser.write((outgoing_command + "\n").encode('utf-8'))
    except Exception as e:
        print("[GCS] Error sending command over serial:", e)

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
        ack_received = {"vehicle_id": command_msg.get("vehicle_id", ""),
                        "status": "no_ack",
                        "command": command_msg.get("command_type", "")}
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
