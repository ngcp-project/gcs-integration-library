#!/usr/bin/env python
import time
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Communication.XBee.XBee import XBee  # Import your XBee wrapper

# --- Configuration ---
# Use the appropriate serial port for the vehicle's XBee.
# On Windows, e.g., "COM3"; on macOS, use the correct /dev/cu.* port.
RECEIVER_PORT = 'COM3'
BAUD_RATE = 115200

# Define this vehicle's numeric code.
# For example, if this vehicle is "ERU", assign 0x01.
MY_VEHICLE_CODE = 0x01

# Create and open the XBee instance.
xbee = XBee(RECEIVER_PORT, BAUD_RATE)
if not xbee.open():
    print("[Vehicle] Could not open XBee on", RECEIVER_PORT)
    exit(1)
print(f"[Vehicle] Opened serial port {RECEIVER_PORT} at {BAUD_RATE} baud.")

def listen_for_commands():
    print("[Vehicle] Listening for minimal binary commands on XBee...")
    while True:
        # Use the XBee wrapper's retrieve_data() to read incoming frames.
        response = xbee.retrieve_data()
        if not response or not hasattr(response, 'data'):
            time.sleep(0.1)
            continue

        data = response.data
        if len(data) < 2:
            continue  # Not enough data for our minimal command.
        
        command_code = data[0]
        vehicle_code = data[1]
        print(f"[Vehicle] Received raw command: {data.hex()}")

        # Decode the command.
        if command_code == 0x01:
            cmd_type = "EMERGENCY_STOP"
        else:
            cmd_type = f"UNKNOWN({command_code})"
        print(f"[Vehicle] Decoded command: {cmd_type}, vehicle code: {vehicle_code:#04x}")

        # Check if this command is for this vehicle.
        if vehicle_code == MY_VEHICLE_CODE:
            print("[Vehicle] Command intended for me. Activating emergency stop!")
            # Place your emergency stop logic here.
            ack = {"vehicle_id": "ERU", "command": "EMERGENCY_STOP", "status": "acknowledged"}
        else:
            print("[Vehicle] Command not for me (vehicle code mismatch).")
            ack = {"vehicle_id": "ERU", "command": cmd_type, "status": "ignored"}

        # Send acknowledgment back as a JSON string (newline-terminated).
        ack_message = json.dumps(ack)
        xbee.transmit_data(ack_message.encode('utf-8'))
        print("[Vehicle] Sent ack:", ack_message)
        time.sleep(0.1)

if __name__ == '__main__':
    listen_for_commands()
