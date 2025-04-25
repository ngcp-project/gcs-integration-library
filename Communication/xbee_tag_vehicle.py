import sys
import threading
import time
from datetime import datetime

# sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')

from Communication.XBee import XBee
from Communication.Frames.x81 import x81
from Communication.tel_struct import Telemetry
from Logger.Logger import Logger

# === Tag Constants ===
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

COMMANDS = {
    1: "KEEP_IN_ZONE",
    2: "EMERGENCY_STOP",
    3: "MOVE_TO_COORD",
    4: "RETURN_HOME"
}

# === Vehicle Setup ===
VEHICLE_NAME = "MRA"  # Change this for each vehicle
GCS_MAC = "0013A20042435A3D"  # MAC of the GCS XBee

logger = Logger(log_to_console=False)
vehicle_xbee = XBee(port="COM4", baudrate=115200, logger=logger)
vehicle_xbee.open()

# === Send Telemetry ===
def send_telemetry():
    while True:
        try:
            telemetry_data = Telemetry(
                speed=45.2, pitch=10.5, yaw=20.3, roll=5.8,
                altitude=1000.0, battery_life=0.80, last_updated=int(datetime.now().timestamp()),
                current_latitude=37.7749, current_longitude=-122.4194,
                vehicle_status=1, patient_status=0,
                message_flag=1, message_lat=45.8484, message_lon=100.4194
            )
            encoded = telemetry_data.encode()
            tagged_payload = bytes([TAG_TELEMETRY]) + encoded
            vehicle_xbee.transmit_data(tagged_payload, address=GCS_MAC)

            print(f"📡 Sent Tagged Telemetry ({len(tagged_payload)} bytes)")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("vehicle_telemetry_log.txt", "a") as log_file:
                log_file.write(f"[{timestamp}] Sent telemetry\n")

            time.sleep(3)

        except Exception as e:
            print(f"[!] Error in send_telemetry: {e}")
            time.sleep(3)

# === Listen for Incoming Commands ===
def listen_for_commands():
    while True:
        try:
            frame: x81 = vehicle_xbee.retrieve_data()
            if not frame:
                time.sleep(0.5)
                continue

            # If it's a Telemetry object (shouldn't happen normally, but just safe check)
            if isinstance(frame.data, Telemetry):
                print("⚡ Unexpected Telemetry received at vehicle side (skipping).")
                continue

            # Otherwise treat it as bytes
            payload = frame.data if isinstance(frame.data, bytes) else frame.data.encode()

            if len(payload) < 1:
                continue

            tag = payload[0]
            body = payload[1:]

            if tag == TAG_COMMAND:
                try:
                    cmd_id = int(body.decode())
                    cmd_name = COMMANDS.get(cmd_id, "UNKNOWN_COMMAND")
                    print(f"📥 Received Command: [{cmd_id}] {cmd_name}")

                    # Respond back with an ACK
                    ack_msg = bytes([TAG_ACK]) + str(cmd_id).encode()
                    vehicle_xbee.transmit_data(ack_msg, address=GCS_MAC)
                    print(f"✅ Sent ACK for command [{cmd_id}] {cmd_name}")

                except ValueError:
                    print(f"[!] Failed to decode command ID: {body}")

            elif tag == TAG_TELEMETRY:
                print("[!] Unexpected Telemetry packet at vehicle side.")

            elif tag == TAG_ACK:
                print(f"✅ Received ACK from GCS: {body.decode(errors='ignore')}")

            else:
                print(f"[!] Unknown tag received: {tag}")

        except Exception as e:
            print(f"[!] Error in listen_for_commands: {e}")

        time.sleep(0.5)

# === Main ===
def main():
    telemetry_thread = threading.Thread(target=send_telemetry, daemon=True)
    command_thread = threading.Thread(target=listen_for_commands, daemon=True)

    telemetry_thread.start()
    command_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down vehicle...")
        vehicle_xbee.close()
        print("✅ Vehicle clean shutdown complete.")

if __name__ == "__main__":
    main()
