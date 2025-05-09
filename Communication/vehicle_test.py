import sys
import threading
import time
from datetime import datetime

sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')

from Communication.XBee import XBee
from Communication.Frames.x81 import x81
from Logger.Logger import Logger

# Vehicle OBC command handlers
# Define or override these functions in your OBC code.
def keep_in_zone():
    print("[OBC] KEEP_IN_ZONE invoked")
    # TODO: implement keep-in-zone logic


def emergency_stop():
    print("[OBC] EMERGENCY_STOP invoked")
    # TODO: implement emergency stop logic


def move_to_coord(lat: float, lon: float):
    print(f"[OBC] MOVE_TO_COORD invoked: lat={lat}, lon={lon}")
    # TODO: implement move to coordinate logic


def return_home():
    print("[OBC] RETURN_HOME invoked")
    # TODO: implement return-home logic

# Constants for XBee tags
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

# Mapping command IDs to handler functions and parameters
COMMAND_HANDLERS = {
    1: (keep_in_zone, ()),
    2: (emergency_stop, ()),
    3: (move_to_coord, ()),  # expects coordinates via separate frame or config
    4: (return_home, ()),
}

# Vehicle Setup
VEHICLE_NAME = "MRA"  # Change to "MRA", "MEA", or "ERU"
GCS_MAC = "0013A200424366C7"  # MAC of the GCS XBee

# Initialize XBee
logger = Logger(log_to_console=False)
vehicle_xbee = XBee(port="COM4", baudrate=115200, logger=logger)
vehicle_xbee.open()

# Telemetry sender thread
def send_telemetry():
    while True:
        payload = chr(TAG_TELEMETRY) + f"{VEHICLE_NAME}::TELEMETRY_PAYLOAD"
        vehicle_xbee.transmit_data(payload, address=GCS_MAC)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("vehicle_telemetry_log.txt", "a") as log_file:
            log_file.write(f"[{timestamp}] {payload[1:]}\n")
        time.sleep(3)

# Command listener thread
def listen_for_commands():
    while True:
        frame: x81 = vehicle_xbee.retrieve_data()
        if frame:
            payload = frame.data.encode() if isinstance(frame.data, str) else frame.data
            tag = payload[0]
            body = payload[1:].decode()

            if tag == TAG_COMMAND:
                try:
                    cmd_id = int(body)
                    handler, args = COMMAND_HANDLERS.get(cmd_id, (None, None))
                    if handler:
                        print(f"Received command ID: {cmd_id}, invoking handler {handler.__name__}")
                        handler(*args)
                    else:
                        print(f"Unknown command ID: {cmd_id}")

                    # Send ACK back to GCS
                    ack_msg = chr(TAG_ACK) + str(cmd_id)
                    vehicle_xbee.transmit_data(ack_msg, address=GCS_MAC)
                    print(f"Sent ACK for command [{cmd_id}]")
                except ValueError:
                    print(f"Failed to decode command ID from body: '{body}'")
        time.sleep(1)

# Main entrypoint
def main():
    telemetry_thread = threading.Thread(target=send_telemetry, daemon=True)
    command_thread = threading.Thread(target=listen_for_commands, daemon=True)

    telemetry_thread.start()
    command_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        vehicle_xbee.close()

if __name__ == "__main__":
    main()
