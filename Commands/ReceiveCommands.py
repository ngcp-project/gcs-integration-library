#!/usr/bin/env python
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Communication.XBee import XBee 

# Configuration for the receiver XBee
RECEIVER_PORT = "/dev/cu.usbserial-D30DWZL5"  # Replace with receiver port
BAUD_RATE = 115200

def main():
    try:
        xbee = XBee(RECEIVER_PORT, BAUD_RATE)
        xbee.open()
        print(f"[+] Receiver XBee opened on {RECEIVER_PORT}")
    except Exception as e:
        print(f"[!] Could not open receiver XBee: {e}")
        return

    print("[*] Waiting for incoming commands...")
    try:
        while True:
            data = xbee.retrieve_data()
            if data:
                print("[<] Received command:", data)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[*] Receiver interrupted by user.")
    except Exception as e:
        print(f"[!] Error reading data: {e}")
    finally:
        xbee.close()
        print("[*] Receiver XBee closed.")

if __name__ == '__main__':
    main()
