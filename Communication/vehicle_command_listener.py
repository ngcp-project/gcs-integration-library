#!/usr/bin/env python
import json
import time
import serial

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB1'  # Adjust for your setup; each vehicle may have its own port
BAUD_RATE = 115200

# Set the vehicle's own identifier (e.g., "ERU", "MEA", etc.)
MY_VEHICLE_ID = "ERU"  # Change as appropriate for each vehicle

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"[Vehicle {MY_VEHICLE_ID}] Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"[Vehicle {MY_VEHICLE_ID}] Error opening serial port:", e)
    exit(1)

def process_command(command):
    """
    Process the received command.
    Expected format:
      {
         "vehicle_id": "ERU",
         "command_type": "EMERGENCY_STOP",
         "command_data": {"emergency": true}
      }
    """
    vehicle = command.get("vehicle_id", "")
    cmd_type = command.get("command_type", "")
    data = command.get("command_data", {})

    # Only process commands intended for this vehicle (or for all vehicles)
    if vehicle != MY_VEHICLE_ID and vehicle.lower() != "all":
        print(f"[Vehicle {MY_VEHICLE_ID}] Command not for me (target: {vehicle}). Ignoring.")
        return None

    ack = {"vehicle_id": MY_VEHICLE_ID, "command": cmd_type, "status": "acknowledged"}
    if cmd_type == "EMERGENCY_STOP":
        print(f"[Vehicle {MY_VEHICLE_ID}] EMERGENCY_STOP activated!")
        # Insert vehicle-specific emergency stop logic here.
    elif cmd_type == "KEEP_IN":
        print(f"[Vehicle {MY_VEHICLE_ID}] KEEP_IN command received. Data: {data}")
    elif cmd_type == "KEEP_OUT":
        print(f"[Vehicle {MY_VEHICLE_ID}] KEEP_OUT command received. Data: {data}")
    else:
        print(f"[Vehicle {MY_VEHICLE_ID}] Unknown command: {cmd_type}")
        ack["status"] = "unknown_command"
    return ack

def main():
    print(f"[Vehicle {MY_VEHICLE_ID}] Listening for commands on XBee...")
    while True:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                command = json.loads(line)
                print(f"[Vehicle {MY_VEHICLE_ID}] Received command:", command)
                ack = process_command(command)
                if ack:
                    ack_message = json.dumps(ack)
                    ser.write((ack_message + "\n").encode('utf-8'))
                    print(f"[Vehicle {MY_VEHICLE_ID}] Sent ack:", ack)
            except Exception as e:
                print(f"[Vehicle {MY_VEHICLE_ID}] Error processing command:", e)
        time.sleep(0.1)

if __name__ == '__main__':
    main()
