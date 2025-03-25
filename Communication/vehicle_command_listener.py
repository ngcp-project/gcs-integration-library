#!/usr/bin/env python
import time
import serial
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Commands.CommandsStruct import Commands  # Import the Commands class

# --- Configuration ---
SERIAL_PORT = '/dev/cu.usbserial-D30DWZKT'  # Adjust as needed for your setup
BAUD_RATE = 115200

# Set the vehicle's own identifier as a numeric code.
# For example, for "ERU", we assign 0x01.
MY_VEHICLE_ID = "ERU"
MY_VEHICLE_CODE = 0x01

# Expected size of the binary command packet, as defined in the Commands structure.
EXPECTED_COMMAND_SIZE = 85

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"[Vehicle {MY_VEHICLE_ID}] Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"[Vehicle {MY_VEHICLE_ID}] Error opening serial port:", e)
    exit(1)

def listen_for_commands():
    print(f"[Vehicle {MY_VEHICLE_ID}] Listening for binary commands on XBee...")
    while True:
        # Read exactly EXPECTED_COMMAND_SIZE bytes.
        data = ser.read(EXPECTED_COMMAND_SIZE)
        if len(data) < EXPECTED_COMMAND_SIZE:
            continue  # Incomplete packet; try again.
        try:
            cmd_obj = Commands.decode(data)
            if not cmd_obj:
                print(f"[Vehicle {MY_VEHICLE_ID}] Failed to decode command packet.")
                continue
            print(f"[Vehicle {MY_VEHICLE_ID}] Decoded command: {cmd_obj}")
        except Exception as e:
            print(f"[Vehicle {MY_VEHICLE_ID}] Error decoding command: {e}")
            continue

        # Check if the command is intended for this vehicle.
        if cmd_obj.vehicle_id != MY_VEHICLE_CODE:
            print(f"[Vehicle {MY_VEHICLE_ID}] Command not for me (received vehicle_id: {cmd_obj.vehicle_id}).")
            ack = {"vehicle_id": MY_VEHICLE_ID, "command": "ignored", "status": "wrong_vehicle"}
        else:
            # Process the command. For an emergency stop, we check the emergency_stop field.
            if cmd_obj.emergency_stop:
                print(f"[Vehicle {MY_VEHICLE_ID}] EMERGENCY_STOP activated!")
                # Insert vehicle-specific emergency stop logic here.
                ack = {"vehicle_id": MY_VEHICLE_ID, "command": "EMERGENCY_STOP", "status": "acknowledged"}
            else:
                print(f"[Vehicle {MY_VEHICLE_ID}] Unknown command received.")
                ack = {"vehicle_id": MY_VEHICLE_ID, "command": "unknown", "status": "ignored"}
        
        # Send acknowledgment as a JSON string (newline-terminated for proper framing).
        ack_message = json.dumps(ack)
        ser.write((ack_message + "\n").encode('utf-8'))
        print(f"[Vehicle {MY_VEHICLE_ID}] Sent ack: {ack}")
        time.sleep(0.1)

if __name__ == '__main__':
    listen_for_commands()
