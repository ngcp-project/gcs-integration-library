#!/usr/bin/env python
import time
import serial
import json

# --- Configuration ---
SERIAL_PORT = '/dev/cu.usbserial-D30DWZKY'  # Adjust for your setup; each vehicle may have its own port
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

def listen_for_commands():
    print(f"[Vehicle {MY_VEHICLE_ID}] Listening for minimal binary commands on XBee...")
    while True:
        waiting = ser.in_waiting
        if waiting:
            print(f"[Vehicle {MY_VEHICLE_ID}] Bytes waiting: {waiting}")
        # Read exactly 2 bytes
        data = ser.read(2)
        if len(data) < 2:
            continue  # Incomplete packet; keep reading.
        command_code = data[0]
        vehicle_code = data[1]
        print(f"[Vehicle {MY_VEHICLE_ID}] Received raw command: {data.hex()}")

        # Decode the command type (0x01 = emergency stop)
        if command_code == 0x01:
            cmd_type = "EMERGENCY_STOP"
        else:
            cmd_type = f"UNKNOWN({command_code})"
        print(f"[Vehicle {MY_VEHICLE_ID}] Decoded command: {cmd_type}, vehicle code: {vehicle_code:#04x}")

        # Process the command only if it is intended for this vehicle.
        if vehicle_code == MY_VEHICLE_CODE:
            if command_code == 0x01:
                print(f"[Vehicle {MY_VEHICLE_ID}] EMERGENCY_STOP activated!")
                # Place your emergency stop logic here.
                ack = {"vehicle_id": MY_VEHICLE_ID, "command": "EMERGENCY_STOP", "status": "acknowledged"}
            else:
                ack = {"vehicle_id": MY_VEHICLE_ID, "command": cmd_type, "status": "unknown_command"}
        else:
            print(f"[Vehicle {MY_VEHICLE_ID}] Command not for me (vehicle code mismatch).")
            ack = {"vehicle_id": MY_VEHICLE_ID, "command": cmd_type, "status": "ignored"}

        # Send acknowledgment as JSON (newline terminated for proper framing).
        ack_message = json.dumps(ack)
        ser.write((ack_message + "\n").encode('utf-8'))
        print(f"[Vehicle {MY_VEHICLE_ID}] Sent ack: {ack}")
        time.sleep(0.1)

if __name__ == '__main__':
    listen_for_commands()
