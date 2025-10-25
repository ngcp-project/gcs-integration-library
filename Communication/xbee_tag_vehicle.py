import sys
import threading
import time
from datetime import datetime

sys.path.insert(1, "../")

from Communication.XBee import XBee
from Communication.Frames.x81 import x81
from Communication.Packet.Telemetry.Telemetry import Telemetry
from Communication.Packet.Command.EmergencyStop import EmergencyStop  # Import command class
from Communication.Packet.Command.CommandResponse import CommandResponse

from Logger.Logger import Logger

# === Tag Constants ===
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03
TAG_PING = 0x04

# === Shared Telemetry Object ===
shared_telemetry = Telemetry()
telemetry_lock = threading.Lock()

# === Vehicle Setup ===
VEHICLE_NAME = "ERU"  # Change this to the current vehicle
GCS_MAC = "0013A200424366C7"  # MAC of the GCS XBee
PORT = "/dev/cu.usbserial-D30DWZL4" # Change this to the current port 
logger = Logger(log_to_console=False)
vehicle_xbee = XBee(port=PORT, baudrate=115200, logger=logger)
vehicle_xbee.open()

flag_count = 0  # Ping counter

# === Update Telemetry with Changing Dummy Data ===
# Every second, incremement speed, pitchm yaw, roll, altitude
# and decrement battery life. Also update latitude and longitude.
# Patient status and message flag are toggled every second.
def update_telemetry():
    while True:
        print("[.] Updating telemetry data...")
        if not hasattr(update_telemetry, "speed"):
            update_telemetry.speed = 0
            update_telemetry.pitch = 0
            update_telemetry.yaw = 0
            update_telemetry.roll = 0
            update_telemetry.altitude = 0
            update_telemetry.battery_life = 100.0
            update_telemetry.current_latitude = 40.0
            update_telemetry.current_longitude = -74.0
            update_telemetry.vehicle_status = 0
            update_telemetry.patient_status = 0
            update_telemetry.message_flag = 0
            update_telemetry.message_lat = 40.0
            update_telemetry.message_lon = -74.0

        update_telemetry.speed += 1
        update_telemetry.pitch += 1
        update_telemetry.yaw += 1
        update_telemetry.roll += 1
        update_telemetry.altitude += 1

        update_telemetry.battery_life -= 0.01
        if update_telemetry.battery_life < 0:
            update_telemetry.battery_life = 100.0

        update_telemetry.current_latitude += 0.0001
        update_telemetry.current_longitude += 0.0001
        
        #update_telemetry.vehicle_status = 1 - update_telemetry.vehicle_status
        
        update_telemetry.patient_status = 1 - update_telemetry.patient_status
        update_telemetry.message_flag = (update_telemetry.message_flag + 1) % 2
        update_telemetry.message_lat += 0.0001
        update_telemetry.message_lon += 0.0001

        # Locks access to shared_telemetry object
        with telemetry_lock:
            shared_telemetry.speed = update_telemetry.speed
            shared_telemetry.pitch = update_telemetry.pitch
            shared_telemetry.yaw = update_telemetry.yaw
            shared_telemetry.roll = update_telemetry.roll
            shared_telemetry.altitude = update_telemetry.altitude
            shared_telemetry.battery_life = update_telemetry.battery_life
            shared_telemetry.current_latitude = update_telemetry.current_latitude
            shared_telemetry.current_longitude = update_telemetry.current_longitude
            shared_telemetry.vehicle_status = update_telemetry.vehicle_status
            shared_telemetry.patient_status = update_telemetry.patient_status
            shared_telemetry.message_flag = update_telemetry.message_flag
            shared_telemetry.message_lat = update_telemetry.message_lat
            shared_telemetry.message_lon = update_telemetry.message_lon
            shared_telemetry.last_updated = datetime.now().timestamp()

        time.sleep(1)
        
# === Send Telemetry ===
# Locks and encodes shared_telemetry. Prefizes encoded bytes with TAG_TELEMETRY
# and sends to GCS. If no ping is received from GCS within 3 seconds,
# increment flag_count. If flag_count >= 3, print warning.
def send_telemetry():
    global flag_count
    logger.write("Starting to send telemetry data...")
    while True:
        with telemetry_lock:
            telemetry_data = shared_telemetry.encode()
        vehicle_xbee.transmit_data(telemetry_data, address=GCS_MAC)

        if flag_count >= 3:
            print("[!] Warning: GCS is disconnected (No 'ping' received)")
            flag_count += 1

        time.sleep(3)
        
# === Listen for Incoming Commands ===
# constant polling of GCS for commands.
# decodes the frame's tag.
def listen_for_commands():
    global flag_count
    while True:
        try:
            frame: x81 = vehicle_xbee.retrieve_data()
            if not frame:
                time.sleep(0.5)
                continue

            payload = frame.data
            if not isinstance(payload, (bytes, bytearray)):
                payload = payload.encode()

            if len(payload) < 1:
                continue

            tag = payload[0]

            
            if tag == TAG_COMMAND:
                
                # decode the emergency stop command
                if len(payload) == 3 and payload[0] == 1 and payload[1] == 3:
                    stop_status = EmergencyStop.decode_packet(payload)
                    with telemetry_lock:
                        shared_telemetry.vehicle_status = 2 if stop_status == 0 else 1 # 2 - emergency mode, 1 - normal

                    
                    command_id = payload[0] 
                    
                    # Construct the ACK packet
                    ack_data = CommandResponse.encode_packet(command_id)
                    ack_payload = bytes([TAG_ACK]) + ack_data
                    
                    # sends the ACK packet back to GCS
                    vehicle_xbee.transmit_data(ack_payload, address=GCS_MAC)
                    state = "ENABLED" if stop_status == 0 else "DISABLED"
                    print(f"✅ Emergency Stop {state}, ACK sent")
                else:
                    print(f"[!] Invalid command format or unsupported commandId: {payload}")

            elif tag == TAG_PING:
                flag_count = 0
                print("📶 Received ping from GCS")

            elif tag == TAG_ACK:
                print(f"✅ Received ACK from GCS: {payload}")

            elif tag == TAG_TELEMETRY:
                print("[!] Received unexpected telemetry from GCS")

            else:
                print(f"[!] Unknown tag: {tag}")

        except Exception as e:
            print(f"[!] Error in listen_for_commands: {e}")
        time.sleep(0.5)

# === Main Entry ===
def main():
    
    # starts 3 daemon threads 
    telemetry_thread = threading.Thread(target=send_telemetry, daemon=True)
    update_thread = threading.Thread(target=update_telemetry, daemon=True)
    command_thread = threading.Thread(target=listen_for_commands, daemon=True)

    telemetry_thread.start()
    update_thread.start()
    command_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down vehicle...")
        vehicle_xbee.close()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()
