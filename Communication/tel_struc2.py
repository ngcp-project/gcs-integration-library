import struct
from datetime import datetime
from typing import Optional

class Telemetry:
    """Handles telemetry data encoding and decoding for UAV/UGV communication."""
    
    def __init__(self, speed=0, pitch=0, yaw=0, roll=0, altitude=0, battery_life=0, 
                 last_updated=None, current_lat=0.0, current_lon=0.0, 
                 vehicle_status=0, message_flag=0, message_lat=0.0, message_lon=0.0):
        self.speed = speed
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.altitude = altitude
        self.battery_life = battery_life
        self.last_updated = int(last_updated.timestamp()) if last_updated else int(datetime.now().timestamp())  # UNIX timestamp
        self.current_lat = current_lat
        self.current_lon = current_lon
        self.vehicle_status = vehicle_status
        self.message_flag = message_flag
        self.message_lat = message_lat
        self.message_lon = message_lon

    def encode(self):
        """Convert telemetry data into a compact binary format for transmission."""
        format_string = "=6fQ2dBB2d"  # Compact binary format
        return struct.pack(format_string, 
                           self.speed, self.pitch, self.yaw, self.roll, 
                           self.altitude, self.battery_life, self.last_updated,
                           self.current_lat, self.current_lon, self.vehicle_status,
                           self.message_flag, self.message_lat, self.message_lon)

    @staticmethod
    def decode(binary_data):
        """Decode binary telemetry data into a Telemetry object."""
        format_string = "=6fQ2dBB2d"
        unpacked_data = struct.unpack(format_string, binary_data)

        # Convert last_updated from integer to datetime
        return Telemetry(
            speed=unpacked_data[0],
            pitch=unpacked_data[1],
            yaw=unpacked_data[2],
            roll=unpacked_data[3],
            altitude=unpacked_data[4],
            battery_life=unpacked_data[5],
            last_updated=datetime.fromtimestamp(unpacked_data[6]),  # Convert int to datetime
            current_lat=unpacked_data[7],
            current_lon=unpacked_data[8],
            vehicle_status=unpacked_data[9],
            message_flag=unpacked_data[10],
            message_lat=unpacked_data[11],
            message_lon=unpacked_data[12]
        )


    def __str__(self):
        """Compact string representation instead of JSON."""
        return f"{self.speed}|{self.pitch}|{self.yaw}|{self.roll}|{self.altitude}|{self.battery_life}|{self.last_updated}|{self.current_lat}|{self.current_lon}|{self.vehicle_status}|{self.message_flag}|{self.message_lat}|{self.message_lon}"

    @staticmethod
    def from_string(data_str):
        """Parse telemetry data from a compact string format."""
        values = data_str.split("|")
        return Telemetry(
            speed=float(values[0]), pitch=float(values[1]), yaw=float(values[2]), roll=float(values[3]),
            altitude=float(values[4]), battery_life=float(values[5]), last_updated=datetime.fromtimestamp(int(values[6])),
            current_lat=float(values[7]), current_lon=float(values[8]), vehicle_status=int(values[9]),
            message_flag=int(values[10]), message_lat=float(values[11]), message_lon=float(values[12])
        )
    

