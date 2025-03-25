#!/usr/bin/env python
import sys
import os
import signal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
from Communication.XBee import XBee
import time
import json
from enum import Enum
from Types.Telemetry import RequestCoordinates
from Types.Geolocation import Coordinate
from Types.Communication import Message
from datetime import datetime
import zlib
from dataclasses import asdict, is_dataclass
from Communication.tel_struct import Telemetry


# Configuration for the sender XBee
# SENDER_PORT = "/dev/cu.usbserial-D30DWZL4"  # Replace with sender port
SENDER_PORT = "COM4"  # Replace with sender port
BAUD_RATE = 115200

# Global flag and data for transmitting
transmit = False
transmit_lock = threading.Lock()

# Flags and Conditions
ping_received = threading.Event()
flag_count = 0
'''-------------------------------------------------------------------------
        TELEMETRY
'''

def custom_serializer(obj):
    """Custom JSON serializer for complex objects."""
    if isinstance(obj, datetime):
        return int(obj.timestamp())  # Convert datetime to UNIX timestamp
    if isinstance(obj, Enum):
        return obj.value  # Convert Enum to integer value
    if hasattr(obj, "to_dict"):  # Custom object handling
        return obj.to_dict()
    raise TypeError(f"Type {type(obj)} not serializable")
    
# VEHICLES sending Telemetry data to GCS
def send_tel(xbee: XBee):
    """Send telemetry data over XBee and wait for acknowledgment."""
    current_coordinate = (37.7749, -122.4194)  # SF Coordinates
    telemetry_data = Telemetry(
        speed=45.2, pitch=10.5, yaw=20.3, roll=5.8,
        altitude=1000.0, battery_life=80, last_updated=int(datetime.now().timestamp()),
        current_latitude=current_coordinate[0], current_longitude=current_coordinate[1],
        vehicle_status=1, message_flag=1, message_lat=45.8484, message_lon=100.4194
    )
    
    # **Binary Transmission (Compact)**
    encoded_data = telemetry_data.encode()
    xbee.transmit_data(encoded_data)
    print(f"Sent Binary {len(encoded_data)} Data bytes)")

    # Receive response
    # time.sleep(0.1)  # Give the receiver time to respond
    # response = xbee.retrieve_data()
    # if response:
    #     print(f"Received Acknowledgment: {response}")
    # else:
    #     print("[!] No acknowledgment received.")


    


# GCS sending PING for ea Telemetry data to VEHICLES
# def send_msg(xbee: XBee):
#     transmit_data = MessageType(dataType="telemetry", messageType="ping")
#     xbee.transmit_data(json.dumps(transmit_data.to_dict()))

# def receive_messages(xbee: XBee):
#     global ping_received
#     try:
#         while True:
#             data = xbee.retrieve_data()
#             if data:
#                 print("Received:", data)
#                 if "ping" in data:
#                     ping_received.set()
#             time.sleep(0.1)
#     except Exception as e:
#         print(f"Error receiving messages: {e}")

'''
-------------------------------------------------------------------------
'''
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

# def manage_serial(xbee):
#     global ping_received
#     try:
#         while True:
#             data = xbee.retrieve_data()
#             if data:
#                 print("Received data:", data)
#                 # If the data is a ping response to telemetry
#                 if data == "Expected ping response":
#                     ping_received.set()
#             time.sleep(0.1)
#     except Exception as e:
#         print(f"Error in serial management: {e}")

def main():
    xbee = XBee(SENDER_PORT, BAUD_RATE)
    xbee.open()

    # Thread for managing serial communication
    # thread_receive = threading.Thread(target=receive_messages, args=(xbee,))
    # thread_send = threading.Thread(target=send_tel, args=(xbee,))

    # # thread_receive.start()
    # thread_send.start()

    # # thread_receive.join()
    # thread_send.join()
    while True:  
        send_tel(xbee)
        time.sleep(3)
    # receive_ping = xbee.retrieve_data()
    # print("=======>\n", receive_ping)

    xbee.close()
    print("[*] Sender XBee closed.")
# def main():
#     try:
#         xbee = XBee(SENDER_PORT, BAUD_RATE)
#         xbee.open()
#         print(f"[+] Sender XBee opened on {SENDER_PORT}")
#     except Exception as e:
#         print(f"[!] Could not open sender XBee: {e}")
#         return

#     t1 = threading.Thread(target=manage_serial, args=(xbee,))
#     t2 = threading.Thread(target=listen_keyboard)
#     t2.start()
#     t1.start()
#     t1.join()
#     t2.join()
#     xbee.close()
#     print("[*] Sender XBee closed.")


if __name__ == '__main__':
    main()
