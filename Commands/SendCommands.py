#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
from Communication.XBee import XBee
import time
import json

# Configuration for the sender XBee
SENDER_PORT = "/dev/cu.usbserial-D30DWZL4"  # Replace with sender port
BAUD_RATE = 115200

# Global flag and data for transmitting
transmit = False
transmit_lock = threading.Lock()
transmit_data = ""

def listen_keyboard():
    global transmit_data, transmit
    try:
        while True:
            # Simulate a command from the UI
            # For example: {"vehicle_name": "eru", "command_type": "KEEP_IN", "command_data": {"param": "dummy"}}
            user_input = input("Enter command (in JSON format): ")
            try:
                # Validate that the input is valid JSON
                cmd = json.loads(user_input)
                # Optionally, reformat or verify command here.
            except Exception as e:
                print(f"Invalid JSON: {e}")
                continue
            transmit_data = user_input  # Keep it as a JSON string
            with transmit_lock:
                transmit = True
    except KeyboardInterrupt:
        print("\n[*] Keyboard interrupt. Exiting sender.")

def manage_serial(xbee: XBee):
    global transmit
    try:
        while xbee is not None and xbee.ser is not None:
            # Check if there's data coming in (if needed)
            data = xbee.retrieve_data()
            if data:
                print("Received (echo/back):", data)
            with transmit_lock:
                if transmit:
                    print("Sending:", transmit_data)
                    xbee.transmit_data(transmit_data)
                    print("Data sent")
                    transmit = False
            time.sleep(0.1)
    except Exception as e:
        print(f"Error in serial management: {e}")
    except KeyboardInterrupt:
        return

def main():
    try:
        xbee = XBee(SENDER_PORT, BAUD_RATE)
        xbee.open()
        print(f"[+] Sender XBee opened on {SENDER_PORT}")
    except Exception as e:
        print(f"[!] Could not open sender XBee: {e}")
        return

    t1 = threading.Thread(target=manage_serial, args=(xbee,))
    t2 = threading.Thread(target=listen_keyboard)
    t2.start()
    t1.start()
    t1.join()
    t2.join()
    xbee.close()
    print("[*] Sender XBee closed.")

if __name__ == '__main__':
    main()
