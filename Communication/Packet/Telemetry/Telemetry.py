import struct

class Telemetry:
    """Handles telemetry data encoding and decoding for UAV/UGV communication."""
    
    def __init__(self, payloadId=2, speed=0, pitch=0, yaw=0, roll=0, altitude=0, battery_life=0, last_updated=0,
             current_latitude=0, current_longitude=0, vehicle_status=0,
             message_flag=0, message_lat=0.0, message_lon=0.0, patient_status=0):
        self.payloadId = 2 # Payload ID for telemetry data is always 2
        self.speed = speed
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.altitude = altitude
        self.battery_life = battery_life
        self.last_updated = last_updated
        self.current_latitude = current_latitude
        self.current_longitude = current_longitude
        self.vehicle_status = vehicle_status  # 1 byte (Status flag 0-255)

        # Message attributes (default: no message)
        self.message_flag = message_flag  # 0 = No Message, 1 = Package, 2 = Patient
        self.message_lat = message_lat
        self.message_lon = message_lon
        self.patient_status = patient_status

    def encode(self):
        """Encode the current Telemetry instance into binary format."""
        format_string = "=B6fd2dBB2dB"
        return struct.pack(format_string, self.payloadId,
                        self.speed, self.pitch, self.yaw, self.roll,
                        self.altitude, self.battery_life, self.last_updated,
                        self.current_latitude, self.current_longitude,
                        self.vehicle_status,
                        self.message_flag,
                        self.message_lat, self.message_lon, self.patient_status)

    @staticmethod
    def decode(binary_data):
        """Decode binary telemetry data into a Telemetry object."""
        expected_size = 68  # Total size of the telemetry packet (in bytes)
        if len(binary_data) != expected_size:
            print(f"Invalid telemetry packet size. Expected {expected_size}, got {len(binary_data)}")
            return None

        format_string = "=B6fd2dBB2dB"
        unpacked_data = struct.unpack(format_string, binary_data)

        return Telemetry(*unpacked_data)

    def __str__(self):
        return (f"Telemetry(Speed={self.speed}, Pitch={self.pitch}, Yaw={self.yaw}, Roll={self.roll}, "
            f"Altitude={self.altitude}, Battery Life={self.battery_life}, Last Updated={self.last_updated}, "
            f"Current Position=({self.current_latitude}, {self.current_longitude}), "
            f"Vehicle Status={self.vehicle_status}, "
            f"Message Flag={self.message_flag}, "
            f"Message Location=({self.message_lat}, {self.message_lon}), "
            f"Patient Status = {self.patient_status}")