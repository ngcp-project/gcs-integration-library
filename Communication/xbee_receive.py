#!/usr/bin/env python
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Communication.XBee import XBee 
from Types.Telemetry import Telemetry, RequestCoordinates, StatusEnum
from Types.Geolocation import Coordinate
from Types.Communication import MessageType, Message
from Telemetry import Telemetry_GCS, RabbitMQ

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
                # parse the received message
                parse_data(data)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[*] Receiver interrupted by user.")
    except Exception as e:
        print(f"[!] Error reading data: {e}")
    finally:
        xbee.close()
        print("[*] Receiver XBee closed.")

def parse_data(data: Message): 
    '''
            TELEMETRY for GCS
    '''
    # GCS receive telemetry data from Vehicles
    # Determine which Vehicle sent
    vehicle_name = ""
    match(data.vehicleId):
        case 1:
            vehicle_name = "ERU"
            
    # parse to determine if this data is 1. Telemetry or 2. Commands
    if(vehicle_name != ""):
        # Case 1. Telemtry:
        if(data.messageType == "Telemetry"):
            #NOTE!: Need to change the "localhost" here
            telemetry = RabbitMQ.TelemetryRabbitMQ(vehicle_name, "localhost") 
            telemetry.publish(data.telemetryData)
        #case 2. Commands. Expecting ACK msg
        elif(data.messageType == "Commands"):
            #NOTE!: Work with Ethan
            return
    else:
        print("\nERROR: Error reading Vehicle Name\n")
    
if __name__ == '__main__':
    main()
