import struct

class Telemetry:
    """Handles telemetry data encoding and decoding for UAV/UGV communication."""
    
    def __init__(self, speed, pitch, yaw, roll, altitude, battery_life, last_updated, 
                 current_latitude, current_longitude, vehicle_status, 
                 message_flag=0, message_lat=0.0, message_lon=0.0):
        self.speed = speed
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.altitude = altitude
        self.battery_life = battery_life
        self.last_updated = last_updated  # Timestamp (8 bytes)
        self.current_latitude = current_latitude
        self.current_longitude = current_longitude
        self.vehicle_status = vehicle_status  # 1 byte (Status flag 0-255)

        # Message attributes (default: no message)
        self.message_flag = message_flag  # 0 = No Message, 1 = Package, 2 = Patient
        self.message_lat = message_lat
        self.message_lon = message_lon

    def encode(self):
        """Convert telemetry data into binary format."""
        
        # 6 floats, 1 Q, 2 doubles, 1 byte, 1 byte, 2 doubles = total 13 items
        format_string = "=6fQ2dBB2d"  
        return struct.pack(format_string, 
                           self.speed, self.pitch, self.yaw, self.roll, 
                           self.altitude, self.battery_life, self.last_updated,
                           self.current_latitude, self.current_longitude, 
                           self.vehicle_status,
                           self.message_flag,  # Indicates whether a message is included
                           self.message_lat, self.message_lon)

    @staticmethod
    def decode(binary_data):
        """Decode binary telemetry data into a Telemetry object."""
        expected_size = 66  # Total size of the telemetry packet (in bytes)
        if len(binary_data) != expected_size:
            print(f"Invalid telemetry packet size. Expected {expected_size}, got {len(binary_data)}")
            return None

        format_string = "=6fQ2dBB2d"
        unpacked_data = struct.unpack(format_string, binary_data)

        return Telemetry(*unpacked_data)

    def __str__(self):
        message_info = (f"Message Type={self.message_flag}, "
                        f"Message Location=({self.message_lat}, {self.message_lon})") if self.message_flag else "No Message"

        return (f"Telemetry(Speed={self.speed}, Pitch={self.pitch}, Yaw={self.yaw}, Roll={self.roll}, "
                f"Altitude={self.altitude}, Battery Life={self.battery_life}, Last Updated={self.last_updated}, "
                f"Current Position=({self.current_latitude}, {self.current_longitude}), "
                f"Vehicle Status={self.vehicle_status}, {message_info})")


# Function to get user input for telemetry data
def get_user_telemetry():
    print("Enter telemetry data:")

    speed = float(input("Speed (m/s): "))
    pitch = float(input("Pitch (degrees): "))
    yaw = float(input("Yaw (degrees): "))
    roll = float(input("Roll (degrees): "))
    altitude = float(input("Altitude (m): "))
    battery_life = float(input("Battery Life (%): "))
    last_updated = int(input("Timestamp (epoch time): "))  # 8-byte unsigned int
    current_latitude = float(input("Current Latitude: "))
    current_longitude = float(input("Current Longitude: "))
    vehicle_status = int(input("Vehicle Status (0-255): "))

    # Ask if there's a message (package/patient location)
    message_flag = int(input("Message Flag (0=No Message, 1=Package, 2=Patient): "))
    if message_flag in [1, 2]:  # If a valid message type is given
        message_lat = float(input("Message Latitude: "))
        message_lon = float(input("Message Longitude: "))
    else:  # No message
        message_lat, message_lon = 0.0, 0.0

    return Telemetry(
        speed, pitch, yaw, roll, altitude, battery_life, last_updated, 
        current_latitude, current_longitude, vehicle_status, 
        message_flag, message_lat, message_lon
    )
    

# The exact size of the telemetry packet with message fields 
print(struct.calcsize("=6fQ2dBB2d"))


# Get telemetry data from the user
telemetry_data = get_user_telemetry()

# Encode telemetry data into bytes
encoded_bytes = telemetry_data.encode()
print(f"\nEncoded Data (Hex): {encoded_bytes.hex()}")

# Decode the telemetry packet back into an object
decoded_telemetry = Telemetry.decode(encoded_bytes)
print("\nDecoded Telemetry Data:")
print(decoded_telemetry)