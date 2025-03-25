#!/usr/bin/env python
import time
import serial
import json

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB1'  # Adjust as needed for your setup; each vehicle may have its own port
BAUD_RATE = 115200

# Set the vehicle's own identifier and corresponding code (e.g., "ERU" → 0x01)
MY_VEHICLE_ID = "ERU"
MY_VEHICLE_CODE = 0x01  # Update this accordingly

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"[Vehicle {MY_VEHICLE_ID}] Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"[Vehicle {MY_VEHICLE_ID}] Error opening serial port:", e)
    exit(1)

def main():
    print(f"[Vehicle {MY_VEHICLE_ID}] Listening for minimal binary commands on XBee...")
    while True:
        # Read exactly 2 bytes
        data = ser.read(2)
        if len(data) < 2:
            continue  # Incomplete packet; keep reading.
        command_code = data[0]
        vehicle_code = data[1]
        print(f"[Vehicle {MY_VEHICLE_ID}] Received raw command: {data.hex()}")
        if command_code == 0x01 and vehicle_code == MY_VEHICLE_CODE:
            print(f"[Vehicle {MY_VEHICLE_ID}] EMERGENCY_STOP activated!")
            ack = {"vehicle_id": MY_VEHICLE_ID, "command": "EMERGENCY_STOP", "status": "acknowledged"}
        else:
            print(f"[Vehicle {MY_VEHICLE_ID}] Received command not intended for me (command_code: {command_code}, vehicle_code: {vehicle_code}).")
            # Optionally ignore and do not send an ack.
            ack = {"vehicle_id": MY_VEHICLE_ID, "command": "unknown", "status": "ignored"}
        # Send acknowledgment as JSON string with newline terminator.
        ack_message = json.dumps(ack)
        ser.write((ack_message + "\n").encode('utf-8'))
        print(f"[Vehicle {MY_VEHICLE_ID}] Sent ack: {ack}")
        time.sleep(0.1)

if __name__ == '__main__':
    main()
