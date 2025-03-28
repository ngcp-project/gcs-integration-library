#!/usr/bin/env python
import time
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Communication.XBee import XBee  # Import your XBee wrapper

# --- Configuration ---
RECEIVER_PORT = '/dev/cu.usbserial-D30DWZKT'  # Adjust as needed
BAUD_RATE = 115200

# Define this vehicle's numeric code.
MY_VEHICLE_CODE = 0x01

# Define the GCS XBee's 64-bit address (update with actual value)
GCS_ADDRESS = "0013A20042435A3D"

xbee = XBee(RECEIVER_PORT, BAUD_RATE)
if not xbee.open():
    print("[Vehicle] Could not open XBee on", RECEIVER_PORT)
    exit(1)
print(f"[Vehicle] Opened serial port {RECEIVER_PORT} at {BAUD_RATE} baud.")

def listen_for_commands():
    print("[Vehicle] Listening for minimal binary commands on XBee...")
    while True:
        response = xbee.retrieve_data()
        if response is None:
            time.sleep(0.1)
            continue

        # Only process received data frames (0x81).
        if not hasattr(response, 'frame_type') or response.frame_type != 0x81:
            time.sleep(0.1)
            continue

        try:
            payload = response.data  # This should be raw bytes for a command packet.
        except AttributeError:
            print("[Vehicle] Received frame without data; ignoring.")
            time.sleep(0.1)
            continue

        # Expect a minimal command (2 bytes)
        if len(payload) != 2:
            print(f"[Vehicle] Received unexpected payload length: {len(payload)} bytes.")
            time.sleep(0.1)
            continue

        command_code = payload[0]
        vehicle_code = payload[1]
        print(f"[Vehicle] Received raw command payload: {payload.hex()}")

        if command_code == 0x01:
            cmd_type = "EMERGENCY_STOP"
        else:
            cmd_type = f"UNKNOWN({command_code})"
        print(f"[Vehicle] Decoded command: {cmd_type}, vehicle code: {vehicle_code:#04x}")

        if vehicle_code == MY_VEHICLE_CODE:
            print(f"[Vehicle] {cmd_type} activated!")
            # Execute vehicle-specific emergency stop logic.
            ack = {"vehicle_id": "ERU", "command": cmd_type, "status": "acknowledged"}
        else:
            print("[Vehicle] Command not for me (vehicle code mismatch).")
            ack = {"vehicle_id": "ERU", "command": cmd_type, "status": "ignored"}

        ack_message = json.dumps(ack)
        try:
            # Send the ack to the GCS by specifying its address.
            xbee.transmit_data(ack_message.encode('utf-8'), address=GCS_ADDRESS)
            print(f"[Vehicle] Sent ack: {ack_message}")
        except Exception as e:
            print(f"[Vehicle] Error sending ack: {e}")
        time.sleep(0.1)

if __name__ == '__main__':
    listen_for_commands()
