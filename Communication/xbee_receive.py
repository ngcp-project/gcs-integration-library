import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Communication.XBee import XBee
from Communication.tel_struct import Telemetry
from Telemetry.RabbitMQ import TelemetryRabbitMQ
import threading
from Communication.Frames import x81, x88, x89


# Configuration
RECEIVER_PORT = "COM5"
BAUD_RATE = 115200

transmit = False
transmit_lock = threading.Lock()
transmit_data = "ping"

vehicle_list = {"eru", "mra", "mea"}

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
        while xbee is not None and xbee.ser is not None:
            received_data = xbee.retrieve_data()

            if received_data:
                # ✅ Process telemetry (x81) messages
                if isinstance(received_data, x81):  
                    print(f"📩 Received Data: {received_data.data}")      
                    parse_pipe_separated_data(received_data)

                    # ✅ Send ping response
                    ping_message = "ping".encode("utf-8")  # Convert to bytes before sending
                    print(f"📤 Sending: {ping_message.decode()}")
                    xbee.transmit_data(ping_message)

                # ✅ Process transmit status (x89) messages
                elif isinstance(received_data, x89):  
                    print(f"📤 Transmit Status Received: Frame ID {received_data.frame_id}, Status {received_data.status}")

                else:
                    print(f"⚠️ Unhandled frame type: {type(received_data)}")

            time.sleep(1)  # Small delay to avoid excessive CPU usage
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
    i = 0
    
    received_telemetry = data.data
    telemetry_dict = {
        "speed": received_telemetry.speed + i,
        "pitch": received_telemetry.pitch + i,
        "yaw": received_telemetry.yaw + i,
        "roll": received_telemetry.roll + i,
        "alt": received_telemetry.altitude + i,
        "battery_life": received_telemetry.battery_life - i/5,
        "lastUpdated": received_telemetry.last_updated + i,
        "current_latitude": received_telemetry.current_latitude + i + 20,
        "current_longitude": received_telemetry.current_longitude + i + 30,
        "vehicle_status": received_telemetry.vehicle_status + i,
        "message_flag": received_telemetry.message_flag + i,
        "message_lat": received_telemetry.message_lat + i,
        "message_lon": received_telemetry.message_lon + i,
    }
    
    for key, value in telemetry_dict.items():
        print(f"{key}: {value}")
                
    match vehicleID:
        case b'\x00\x00':
            vehicle_name = "eru"
    print(f"\nVehicle Name: {vehicle_name.capitalize()}")

    for vehicle in vehicle_list:
        telemetry = TelemetryRabbitMQ(f"{vehicle}", "localhost")
        telemetry.publish(telemetry_dict)

if __name__ == '__main__':
    main()
