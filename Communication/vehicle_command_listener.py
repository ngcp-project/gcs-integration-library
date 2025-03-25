#!/usr/bin/env python
import time
import serial
from Commands.CommandsStruct import Commands
import json

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB1'  # Adjust for your setup; each vehicle may have its own port
BAUD_RATE = 115200

# Set the vehicle's own identifier (e.g., "ERU", "MEA", etc.)
MY_VEHICLE_ID = "ERU"  # Change as appropriate for each vehicle

# Expected size of the binary command message
COMMAND_MSG_SIZE = 84

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"[Vehicle {MY_VEHICLE_ID}] Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"[Vehicle {MY_VEHICLE_ID}] Error opening serial port:", e)
    exit(1)

def read_full_message(ser, size):
    """Read exactly 'size' bytes from the serial port, or timeout after 5 seconds."""
    data = b""
    start_time = time.time()
    while len(data) < size and time.time() - start_time < 5:
        chunk = ser.read(size - len(data))
        if not chunk:
            continue
        data += chunk
    return data

def process_command(cmd_obj):
    """
    Process the received binary command (as a Commands object).
    For now, we assume that a binary command with emergency_stop == True
    means this vehicle should perform an emergency stop.
    """
    if cmd_obj.emergency_stop:
        print(f"[Vehicle {MY_VEHICLE_ID}] EMERGENCY_STOP activated!")
        # Insert vehicle-specific emergency stop logic here.
        ack = {"vehicle_id": MY_VEHICLE_ID, "command": "EMERGENCY_STOP", "status": "acknowledged"}
    else:
        print(f"[Vehicle {MY_VEHICLE_ID}] Received unknown binary command.")
        ack = {"vehicle_id": MY_VEHICLE_ID, "command": "unknown", "status": "unknown_command"}
    return ack

def main():
    print(f"[Vehicle {MY_VEHICLE_ID}] Listening for binary commands on XBee...")
    while True:
        data = read_full_message(ser, COMMAND_MSG_SIZE)
        if len(data) < COMMAND_MSG_SIZE:
            # Not enough bytes received – wait for next message
            continue
        try:
            cmd_obj = Commands.decode(data)
            if not cmd_obj:
                print(f"[Vehicle {MY_VEHICLE_ID}] Failed to decode binary command.")
                continue
            print(f"[Vehicle {MY_VEHICLE_ID}] Received command: {cmd_obj}")
            ack = process_command(cmd_obj)
            # Send ack as JSON string (newline terminated for framing)
            ack_message = json.dumps(ack)
            ser.write((ack_message + "\n").encode('utf-8'))
            print(f"[Vehicle {MY_VEHICLE_ID}] Sent ack: {ack}")
        except Exception as e:
            print(f"[Vehicle {MY_VEHICLE_ID}] Error processing binary command:", e)
        time.sleep(0.1)

if __name__ == '__main__':
    main()
