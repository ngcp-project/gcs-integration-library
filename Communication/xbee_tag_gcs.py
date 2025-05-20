import json
import sys
import threading
import time
from datetime import datetime

sys.path.insert(1, "../")

from Communication.XBee import XBee
from Communication.Frames import x81
# from Communication.tel_struct import Telemetry
from Communication.Packet.Telemetry.Telemetry import Telemetry
from Logger.Logger import Logger
from Telemetry.RabbitMQ import TelemetryRabbitMQ

TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03
TAG_PING = 0x04

VEHICLES = {
    "MRA": {"MAC": "0013A200424353F7", "short": "0002"},
    "ERU": {"MAC": "0013A20042435EA9", "short": "0003"},
    # "MEA": {"MAC": "0013A2004243672F", "short": "0004"}
}

# TO DO: Update after command structure is finalized
COMMANDS = {
    1: "KEEP_IN_ZONE",
    2: "EMERGENCY_STOP",
    3: "MOVE_TO_COORD",
    4: "RETURN_HOME"
}

PORT = "/dev/cu.usbserial-D30DWZKT"
# PORT = "/dev/ttyUSB0" # For Linux


logger = Logger(log_to_console=True)
gcs_xbee = XBee(port=PORT, baudrate=115200, logger=logger)
gcs_xbee.open()

terminate_event = threading.Event()
telemetry_publishers = {}

def get_or_create_publisher(vehicle_name):
    if vehicle_name not in telemetry_publishers:
        telemetry_publishers[vehicle_name] = TelemetryRabbitMQ(vehicle_name.lower(), "localhost")
    return telemetry_publishers[vehicle_name]

def parse_and_export_telemetry(telemetry: Telemetry, vehicle_name: str, rssi: int):
    telemetry_dict = {
        "speed": telemetry.speed,
        "pitch": telemetry.pitch,
        "yaw": telemetry.yaw,
        "roll": telemetry.roll,
        "alt": telemetry.altitude,
        "battery_life": telemetry.battery_life,
        "lastUpdated": telemetry.last_updated,
        "current_latitude": telemetry.current_latitude,
        "current_longitude": telemetry.current_longitude,
        "vehicle_status": telemetry.vehicle_status,
        "patient_status": telemetry.patient_status,
        "message_flag": telemetry.message_flag,
        "message_lat": telemetry.message_lat,
        "message_lon": telemetry.message_lon,
    }

    try:
        publisher = get_or_create_publisher(vehicle_name)
        publisher.publish(telemetry_dict)
        export_rssi(vehicle_name, rssi)
        logger.write(f"✅ Published telemetry for {vehicle_name}")
    except Exception as e:
        import traceback
        logger.write(f"[!] Failed to publish telemetry for {vehicle_name}: {e}")
        logger.write(traceback.format_exc())

def listen_for_telemetry():
    while not terminate_event.is_set():
        try:
            frame: x81 = gcs_xbee.retrieve_data()
            if not frame:
                time.sleep(0.05)
                continue

            src_16bit = frame.source_address.hex().upper().zfill(4)
            vehicle_name = next((name for name, info in VEHICLES.items() if info["short"] == src_16bit), "UNKNOWN")

            if isinstance(frame.data, Telemetry):
                telemetry = frame.data
            elif isinstance(frame.data, bytes) and frame.data[0] == TAG_TELEMETRY:
                try:
                    telemetry = Telemetry.decode(frame.data)
                except Exception as e:
                    logger.write(f"[!] Failed to decode raw telemetry: {e}")
                    continue
            else:
                if isinstance(frame.data, bytes) and frame.data[0] == TAG_ACK:
                    logger.write(f"✅ Received ACK from {vehicle_name}: {frame.data[1:].decode(errors='ignore')}")
                else:
                    logger.write(f"[!] Unknown data from {vehicle_name}")
                continue

            logger.write(f"📡 Telemetry from {vehicle_name} (RSSI: {frame.rssi})")
            logger.write(f"Telemetry Data: {telemetry}")
            parse_and_export_telemetry(telemetry, vehicle_name, frame.rssi)

            # Send ping back
            ping_payload = bytes([TAG_PING])
            mac = VEHICLES.get(vehicle_name, {}).get("MAC")
            if mac and mac != "NaN":
                try:
                    gcs_xbee.transmit_data(ping_payload, address=mac)
                    logger.write(f"📶 Sent PING to {vehicle_name}")
                except Exception as e:
                    logger.write(f"[!] Error sending PING: {e}")

        except Exception as e:
            logger.write(f"[!] Error in listen_for_telemetry: {e}")
            time.sleep(0.2)
            
def export_rssi(vehicle_name: str, rssi: int):
    try:
        publisher = get_or_create_publisher(vehicle_name)
        rssi_payload = {
            "vehicle": vehicle_name,
            "rssi": rssi,
            "timestamp": datetime.now().isoformat()
        }
        publisher.channel.queue_declare(queue=f"rssi_{vehicle_name.lower()}")
        publisher.channel.basic_publish(
            exchange='',
            routing_key=f"rssi_{vehicle_name.lower()}",
            body=json.dumps(rssi_payload)
        )
        logger.write(f"📶 Published RSSI for {vehicle_name}: {rssi} dBm")
    except Exception as e:
        logger.write(f"[!] Failed to publish RSSI for {vehicle_name}: {e}")


def shutdown():
    terminate_event.set()
    gcs_xbee.close()
    for pub in telemetry_publishers.values():
        pub.close_connection()
    logger.write("✅ GCS shutdown complete.")

def main():
    telemetry_thread = threading.Thread(target=listen_for_telemetry, daemon=True)
    telemetry_thread.start()

    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        logger.write("\n🛑 Shutdown requested by user.")
    finally:
        shutdown()

if __name__ == "__main__":
    main()
