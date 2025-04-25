import sys
import threading
import time
from datetime import datetime

sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')

from Communication.XBee import XBee
from Communication.Frames import x81
from Communication.tel_struct import Telemetry
from Logger.Logger import Logger

# === Constants ===
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

# === Vehicle Info ===
VEHICLES = {
    "MRA": {"MAC": "0013A20042435EA9", "short": "0002"},
    "ERU": {"MAC": "NaN", "short": "0003"},
    "MEA": {"MAC": "0013A2004243672F", "short": "0004"}
}

COMMANDS = {
    1: "KEEP_IN_ZONE",
    2: "EMERGENCY_STOP",
    3: "MOVE_TO_COORD",
    4: "RETURN_HOME"
}

# === Init GCS XBee ===
logger = Logger(log_to_console=False)
# gcs_xbee = XBee(port="/dev/cu.usbserial-D30DWZKT", baudrate=115200, logger=logger)
gcs_xbee = XBee(port="COM3", baudrate=115200, logger=logger)
gcs_xbee.open()
terminate_event = threading.Event()


# === Telemetry Receiver ===
def listen_for_telemetry():
    while not terminate_event.is_set():
        frame: x81 = gcs_xbee.retrieve_data()
        if frame:
            src_16bit = frame.source_address.hex().upper().zfill(4)
            print(f"📍 Incoming packet short address: {src_16bit}")
            
            vehicle_name = next((name for name, info in VEHICLES.items() if info["short"] == src_16bit), "UNKNOWN")

            if isinstance(frame.data, Telemetry):
                telemetry = frame.data
                print(f"📡 [Telemetry] From: {vehicle_name} ({src_16bit}), RSSI: {frame.rssi}")
                print(telemetry)

                timestamp = datetime.now().isoformat(timespec="seconds")
                with open("gcs_telemetry_log.txt", "a") as log_file:
                    log_file.write(f"{timestamp} | Telemetry from {vehicle_name} ({src_16bit}) | RSSI: {frame.rssi}\n")
                    log_file.write(f"{telemetry}\n\n")

            elif isinstance(frame.data, bytes) and frame.data[0] == TAG_ACK:
                print(f"✅ Received ACK from {vehicle_name} ({src_16bit}): {frame.data[1:].decode(errors='ignore')}")
            else:
                print(f"[!] Unknown or unhandled data from {vehicle_name}")


        time.sleep(0.05)

def main():
    telemetry_thread = threading.Thread(target=listen_for_telemetry, daemon=True)
    telemetry_thread.start()

    try:
        while True:
            print("\n📡 GCS Command Center")
            print("Available Vehicles:", ", ".join(VEHICLES.keys()))
            # vehicle_name = input("Enter vehicle name (or 'exit' to quit): ").strip().upper()
            vehicle_name = "MRA"

            if vehicle_name == 'EXIT':
                break

            if vehicle_name not in VEHICLES:
                print("❌ Invalid vehicle name.")
                continue

            vehicle = VEHICLES[vehicle_name]
            if vehicle["MAC"] == "NaN":
                print("❌ MAC address not set for this vehicle.")
                continue

            print("🛠️ Available Commands:")
            for cmd_id, cmd_name in COMMANDS.items():
                print(f" {cmd_id}: {cmd_name}")

            try:
                # command_id = int(input("Enter Command ID: "))
                command_id = 1
                if command_id not in COMMANDS:
                    print("❌ Invalid Command ID")
                    continue
            except ValueError:
                print("❌ Invalid input")
                continue

            payload = bytes([TAG_COMMAND]) + str(command_id).encode()
            print(f"📤 Sending '{COMMANDS[command_id]}' to {vehicle_name}...")
            gcs_xbee.transmit_data(payload, address=vehicle["MAC"])
            print("✅ Command sent.")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Exiting GCS...")

    finally:
        print("🛑 Cleaning up...")
        terminate_event.set()
        gcs_xbee.close()
        time.sleep(0.5)
        print("✅ Clean shutdown complete.")



if __name__ == "__main__":
    main()



# import re
# import serial
# import time
# from Communication.interfaces.Serial import Serial
# from Communication.Frames import x81, x88, x89
# from Logger.Logger import Logger
# from Communication.tel_struct import Telemetry

# # NOTE** Might need to check data length
#     def __encode_data(self, data, address = "0000000000000000"):
#         """Encode String data.

#         Args: 
#           data: String data to encode.
#           address: Address of destination XBee module. "0000000000000000" if no value is provided.
#         Returns:
#           Framed String data.
#         """
#         frame = bytearray()
#         frame.append(0x7E)  # Start delimiter (1 byte)
#         frame.append(((len(data) + 11) // 256))  # Length (2 bytes)
#         frame.append((len(data) + 11) % 256)
#         frame.append(0x00)  # Frame type (1 byte)
#         frame.append(self.frame_id)  # Frame ID (1 bytes)
#         self.frame_id = self.frame_id % 0xff + 0x01

#         for i in range(8):  # 64-bit address (8 bytes)
#             frame.append(int(address[2 * i : 2 * i + 2], 16))

#         frame.append(0x00)  # Options (1 byte)
#         frame.extend(data)  # RF data (0 - 256 bytes)
#         # FF - number of bytes between length & checksum field
#         checksum = 0xFF - (sum(frame[3:]) & 0xFF)
#         frame.append(checksum)  # Checksum (1 byte)

#         # print(frame)
#         print("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))
#         self.logger.write("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))

#         return frame
    
#     def __0x81(self, frame_data) -> x81:
#         """Handle XBee Frame Type 81 (Frame Receive: 16-bit Address)

#         Args:
#           frame_data: Received bytes (between length and checksum fields)

#         Returns:
#           xxxxDecoded message & Received Signal Strength Indicator (RSSI), None if there is an error decoding message
#           Returns 0x81 class (frame_type, frame_id, payload, rssi, ...)
#         """
#         frame_type = frame_data[0]
#         source_address = frame_data[1:3]
#         rssi = -frame_data[3]
#         options = frame_data[4]
#         data = frame_data[5:]
#         try:
#             if len(data) == 66:
#                 # ✅ Use Telemetry.decode() if the message is exactly 66 bytes
#                 decoded_message = Telemetry.decode(data)
#                 self.logger.write(f"✅ Using Telemetry.decode(). RSSI: {rssi}, Decoded message: {decoded_message}")
#             else:
#                 # 🚨 Handle other cases: data is not 66 bytes
#                 decoded_message = data.decode()  # Keep as raw bytes or implement another parsing function
#                 self.logger.write(f"⚠️ Message length is {len(data)} bytes, not 66. Skipping Telemetry.decode().")
#             self.logger.write(f"Received payload. RSSI: {rssi}, Decoded message: {decoded_message}")
#             print(f"RSSI (Signal Strength : {rssi} dBm)")
#             print("Decoded message:", decoded_message)
#             #print("RSSI:", rssi)    
#             frame = x81(frame_type, source_address, rssi, options, decoded_message)
#             self.logger.write(f"[Frame Receive: 16-bit Address] Frame Type: {frame.frame_type}, Source Address: {frame.source_address}, RSSI: {frame.rssi}, Options: {frame.options}, Data: {frame_data}")
#             print(f"[Frame Receive: 16-bit Address] Frame Type: {frame.frame_type}, Source Address: {frame.source_address}, RSSI: {frame.rssi}, Options: {frame.options}, Data: {frame_data}")
#             return frame
#         except UnicodeDecodeError:
#             self.logger.write(f"Error decoding payload. RSSI: {rssi}")
#             print("Error decoding payload")
#             return None
