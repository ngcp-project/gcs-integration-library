#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
from Communication.XBee import XBee
import time
import json
from Types.Telemetry import Telemetry, RequestCoordinates, StatusEnum
from Types.Geolocation import Coordinate
from Types.Communication import MessageType, Message
from datetime import datetime

# Configuration for the sender XBee
SENDER_PORT = "/dev/cu.usbserial-D30DWZL4"  # Replace with sender port
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
# VEHICLES sending Telemetry data to GCS
def send_tel(xbee: XBee) :
    global ping_received
    global flag_count
    ping_received.clear()
    current_coordinate = Coordinate(latitude=37.7749, longitude=-122.4194)
    request_location = Coordinate(latitude=45.8484, longitude=100.4194)
    request_coordinates = RequestCoordinates(requestLocation=request_location, requestDescription="package")
    message_type = MessageType(dataType="telemetry", messageType="data")

    try:
        while True:
            try: 
                tel_data = Telemetry(
                    localIP="12.12.12.12",
                    pitch=10.5,
                    yaw=20.3,
                    roll=5.8,
                    speed=45.2,
                    altitude=1000.0,
                    batteryLife=80.5,
                    currentPosition=current_coordinate,
                    lastUpdated=datetime.now(),
                    fireFound=False,
                    requestCoord=request_coordinates
                )
                transmit_data = Message(messageType=message_type, telemetryData=tel_data)
                xbee.transmit_data(json.dumps(transmit_data.to_dict()))
                
                if not ping_received.wait(1): 
                    flag_count += 1
                    print(f"Ping response not received within 1 second. Flag Count {flag_count}\n")
                else:
                    print("Ping received successfully.")
                
                ping_received.clear()
                time.sleep(3) #NOTE!: need to change this for Telemetry Sending Interval
            except Exception as e:
                print(f"Error Sending Message: {e}")
                continue
    except KeyboardInterrupt:
        print("\n[*] Keyboard interrupt. Exiting sender.")

# GCS sending PING for ea Telemetry data to VEHICLES
def send_msg(xbee: XBee):
    transmit_data = MessageType(dataType="telemetry", messageType="ping")
    xbee.transmit_data(json.dumps(transmit_data.to_dict()))

def receive_messages(xbee: XBee):
    global ping_received
    try:
        while True:
            data = xbee.retrieve_data()
            if data:
                print("Received:", data)
                if "ping" in data:
                    ping_received.set()
            time.sleep(0.1)
    except Exception as e:
        print(f"Error receiving messages: {e}")

'''
-------------------------------------------------------------------------
'''
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

def manage_serial(xbee):
    global ping_received
    try:
        while True:
            data = xbee.retrieve_data()
            if data:
                print("Received data:", data)
                # If the data is a ping response to telemetry
                if data == "Expected ping response":
                    ping_received.set()
            time.sleep(0.1)
    except Exception as e:
        print(f"Error in serial management: {e}")

def main():
    xbee = XBee(SENDER_PORT, BAUD_RATE)
    xbee.open()

    # Thread for managing serial communication
    thread_receive = threading.Thread(target=receive_messages, args=(xbee,))
    thread_send = threading.Thread(target=send_tel, args=(xbee,))

    thread_receive.start()
    thread_send.start()

    thread_receive.join()
    thread_send.join()

    xbee.close()
    print("[*] Sender XBee closed.")

if __name__ == '__main__':
    main()
