import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Communication.XBee import XBee
from Communication.tel_struct import Telemetry
from Telemetry.RabbitMQ import TelemetryRabbitMQ

# Configuration
RECEIVER_PORT = "COM3"
BAUD_RATE = 115200

def main():
    """
    Main function to initialize XBee receiver and process incoming messages.
    """
    try:
        xbee = XBee(RECEIVER_PORT, BAUD_RATE)
        if not xbee.open():
            print(f"[!] Failed to open XBee on {RECEIVER_PORT}")
            return

        print(f"[+] Receiver XBee opened on {RECEIVER_PORT}")
    except Exception as e:
        print(f"[!] Could not open receiver XBee: {e}")
        return

    print("[*] Waiting for incoming telemetry data...")

    try:
        while True:
            received_data = xbee.retrieve_data()            
            if received_data is None:
                continue
            
            print(f"Received Data: {received_data.data}")         
               
            parse_pipe_separated_data(received_data)
            
            # Send acknowledgment back to sender
            # ack_message = f"ACK: Received bytes"
            # xbee.transmit_data(ack_message.encode())
            # print(f"Sent Acknowledgment: {ack_message}")

            time.sleep(0.1)  # Small delay to avoid excessive CPU usage
    except KeyboardInterrupt:
        print("\n[*] Receiver interrupted by user.")
    except Exception as e:
        print(f"[!] Error reading data: {e}")
    finally:
        xbee.close()
        print("[*] Receiver XBee closed.")

def parse_pipe_separated_data(data):
    
    vehicleID = data.source_address
    vehicle_name = ""
    
    received_telemetry = data.data
    telemetry_dict = {
        "Speed (m/s)": received_telemetry.speed,
        "Pitch (°)": received_telemetry.pitch,
        "Yaw (°)": received_telemetry.yaw,
        "Roll (°)": received_telemetry.roll,
        "Altitude (m)": received_telemetry.altitude,
        "Battery Life (%)": received_telemetry.battery_life,
        "Timestamp": received_telemetry.last_updated,
        "Latitude": received_telemetry.current_latitude,
        "Longitude": received_telemetry.current_longitude,
        "Vehicle Status": received_telemetry.vehicle_status,
        "Message Type": received_telemetry.message_flag,
        "Message Latitude": received_telemetry.message_lat,
        "Message Longitude": received_telemetry.message_lon,
    }
    
    for key, value in telemetry_dict.items():
        print(f"{key}: {value}")
                
    match vehicleID:
        case b'\x00\x00':
            vehicle_name = "eru"
    print(f"\nVehicle Name: {vehicle_name.capitalize()}")

    telemetry = TelemetryRabbitMQ(f"{vehicle_name}", "localhost")
    telemetry.publish(telemetry_dict)

if __name__ == '__main__':
    main()
