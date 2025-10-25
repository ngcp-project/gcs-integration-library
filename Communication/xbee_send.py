#!/usr/bin/env python
import sys
import os
import threading
import time
import json
from datetime import datetime
from Communication.XBee import XBee
from Communication.tel_struct import Telemetry

# Configuration for the sender XBee
SENDER_PORT = "COM4"  # Replace with your sender port
BAUD_RATE = 115200

# Global event for clean shutdown
terminate_event = threading.Event()

# Global variables for transmitting messages
transmit_data = ""
transmit_lock = threading.Lock()
transmit_flag = threading.Event()  # Used for signaling data transmission
flag_count = 0  # Counter for missed responses

def send_tel(xbee: XBee):
    """
    Sends telemetry data every 3 seconds and keeps track of missed "ping" responses.
    """
    global flag_count

    while not terminate_event.is_set():
        try:
            # Create telemetry data
            current_coordinate = (37.7749, -122.4194)  # SF Coordinates
            telemetry_data = Telemetry(
                speed=45.2, pitch=10.5, yaw=20.3, roll=5.8,
                altitude=1000.0, battery_life=.80, last_updated=int(datetime.now().timestamp()),
                current_latitude=current_coordinate[0], current_longitude=current_coordinate[1],
                vehicle_status=1, message_flag=1, message_lat=45.8484, message_lon=100.4194
            )

            encoded_data = telemetry_data.encode()
            xbee.transmit_data(encoded_data)
            print(f"✅ Sent Telemetry Data ({len(encoded_data)} bytes)")

            # Check if we have missed 10 consecutive "ping" responses
            if flag_count >= 10:
                print("[!] Warning: GCS is disconnected (No 'ping' received for 10 telemetry messages)")

            time.sleep(3)  # Wait before sending again

        except Exception as e:
            print(f"[!] Error sending telemetry: {e}")

def receive_messages(xbee: XBee):
    """
    Continuously listens for incoming messages and resets flag_count when "ping" is received.
    """
    global flag_count
    while not terminate_event.is_set():
        try:
            data = xbee.retrieve_data()
            
            if data:
                print(f"📩 Received Data: {data}")

                # If we receive a "ping", reset flag_count
                if "ping" in data:
                    flag_count = 0
                else:
                    flag_count += 1  # Increment counter for messages that are NOT "ping"

            time.sleep(0.5)  # Small delay to reduce CPU usage
        except Exception as e:
            print(f"[!] Error receiving messages: {e}")

def listen_keyboard():
    """
    Listens for user input and sets the data to be transmitted.
    """
    global transmit_data

    try:
        while not terminate_event.is_set():
            user_input = input("💻 Enter command (in JSON format): ").strip()
            if user_input:
                try:
                    # Validate JSON format
                    json.loads(user_input)
                    with transmit_lock:
                        transmit_data = user_input
                        transmit_flag.set()  # Signal that data is ready to be sent
                except json.JSONDecodeError:
                    print("[!] Invalid JSON format. Please enter a valid JSON string.")

    except KeyboardInterrupt:
        print("\n[*] Keyboard input stopped.")
    finally:
        terminate_event.set()  # Ensure all threads stop

def transmit_user_command(xbee: XBee):
    """
    Sends user-entered commands from the keyboard.
    """
    while not terminate_event.is_set():
        try:
            if transmit_flag.is_set():
                with transmit_lock:
                    print(f"📤 Sending user command: {transmit_data}")
                    xbee.transmit_data(transmit_data)
                    transmit_flag.clear()  # Reset flag after sending

            time.sleep(1)  # Prevent excessive CPU usage
        except Exception as e:
            print(f"[!] Error transmitting user command: {e}")

def main():
    """
    Initializes XBee and starts send/receive threads.
    """
    xbee = XBee(SENDER_PORT, BAUD_RATE)

    if not xbee.open():
        print(f"[!] Failed to open XBee on {SENDER_PORT}")
        return

    print(f"[+] XBee opened on {SENDER_PORT}")

    # Start telemetry sender thread
    send_thread = threading.Thread(target=send_tel, args=(xbee,))
    send_thread.daemon = True
    send_thread.start()

    # Start message receiver thread
    receive_thread = threading.Thread(target=receive_messages, args=(xbee,))
    receive_thread.daemon = True
    receive_thread.start()

    # Start keyboard listener thread
    keyboard_thread = threading.Thread(target=listen_keyboard)
    keyboard_thread.daemon = True
    keyboard_thread.start()

    # Start user command transmission thread
    user_command_thread = threading.Thread(target=transmit_user_command, args=(xbee,))
    user_command_thread.daemon = True
    user_command_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep main thread alive
    except KeyboardInterrupt:
        print("\n[*] Stopping all threads and closing XBee.")
        terminate_event.set()  # Signal all threads to exit
        xbee.close()

if __name__ == '__main__':
    main()
