import struct

class Commands:
    """
    A class to encode and decode command messages.
    
    Fields:
      - emergency_stop (bool): Emergency stop command.
      - autonomous_enabled (bool): Whether autonomous mode is enabled.
      - mission_lat (float): Latitude of the mission target (e.g. hiker/package location).
      - mission_lon (float): Longitude of the mission target.
      - keep_in_flag (bool): Indicates if a keep-in zone is defined.
      - keep_in_coord1 (tuple of two floats): First coordinate (e.g. lower left) of the keep-in rectangle.
      - keep_in_coord2 (tuple of two floats): Second coordinate (e.g. upper right) of the keep-in rectangle.
      - keep_out_flag (bool): Indicates if a keep-out zone is defined.
      - keep_out_coord1 (tuple of two floats): First coordinate of the keep-out rectangle.
      - keep_out_coord2 (tuple of two floats): Second coordinate of the keep-out rectangle.
      
    The binary packet uses the format string: "=2B2dB4dB4d"
      - 2B: emergency_stop and autonomous_enabled (each 1 byte)
      - 2d: mission_lat, mission_lon (each 8 bytes)
      - B: keep_in_flag (1 byte)
      - 4d: Two coordinates for keep-in zone (4 doubles)
      - B: keep_out_flag (1 byte)
      - 4d: Two coordinates for keep-out zone (4 doubles)
    Total size: 2 + 16 + 1 + 32 + 1 + 32 = 84 bytes.
    """
    def __init__(self, emergency_stop, autonomous_enabled, mission_lat, mission_lon,
                 keep_in_flag=0, keep_in_coord1=(0.0, 0.0), keep_in_coord2=(0.0, 0.0),
                 keep_out_flag=0, keep_out_coord1=(0.0, 0.0), keep_out_coord2=(0.0, 0.0)):
        self.emergency_stop = emergency_stop
        self.autonomous_enabled = autonomous_enabled
        self.mission_lat = mission_lat
        self.mission_lon = mission_lon
        self.keep_in_flag = keep_in_flag
        self.keep_in_coord1 = keep_in_coord1
        self.keep_in_coord2 = keep_in_coord2
        self.keep_out_flag = keep_out_flag
        self.keep_out_coord1 = keep_out_coord1
        self.keep_out_coord2 = keep_out_coord2

    def encode(self):
        """
        Encode the command data into a binary packet.
        """
        format_string = "=2B2dB4dB4d"
        # Convert booleans to integers (0 or 1)
        es = 1 if self.emergency_stop else 0
        ae = 1 if self.autonomous_enabled else 0
        kin = 1 if self.keep_in_flag else 0
        kout = 1 if self.keep_out_flag else 0
        # Pack keep_in zone as 4 doubles: (lat1, lon1, lat2, lon2)
        kin_values = (self.keep_in_coord1[0], self.keep_in_coord1[1],
                      self.keep_in_coord2[0], self.keep_in_coord2[1])
        # Similarly for keep_out zone
        kout_values = (self.keep_out_coord1[0], self.keep_out_coord1[1],
                       self.keep_out_coord2[0], self.keep_out_coord2[1])
        return struct.pack(format_string,
                           es, ae,
                           self.mission_lat, self.mission_lon,
                           kin,
                           *kin_values,
                           kout,
                           *kout_values)

    @staticmethod
    def decode(binary_data):
        """
        Decode a binary command packet into a Commands object.
        """
        format_string = "=2B2dB4dB4d"
        expected_size = struct.calcsize(format_string)
        if len(binary_data) != expected_size:
            print(f"Invalid command packet size. Expected {expected_size}, got {len(binary_data)}")
            return None
        unpacked = struct.unpack(format_string, binary_data)
        # Unpack the fields:
        # (emergency_stop, autonomous_enabled, mission_lat, mission_lon, keep_in_flag, 4 doubles, keep_out_flag, 4 doubles)
        es, ae, mlat, mlon, kin_flag = unpacked[0], unpacked[1], unpacked[2], unpacked[3], unpacked[4]
        kin_vals = unpacked[5:9]
        kout_flag = unpacked[9]
        kout_vals = unpacked[10:14]
        kin_coord1 = (kin_vals[0], kin_vals[1])
        kin_coord2 = (kin_vals[2], kin_vals[3])
        kout_coord1 = (kout_vals[0], kout_vals[1])
        kout_coord2 = (kout_vals[2], kout_vals[3])
        return Commands(bool(es), bool(ae), mlat, mlon,
                        kin_flag, kin_coord1, kin_coord2,
                        kout_flag, kout_coord1, kout_coord2)

    def __str__(self):
        return (f"Commands(EmergencyStop={self.emergency_stop}, AutonomousEnabled={self.autonomous_enabled}, "
                f"Mission=({self.mission_lat}, {self.mission_lon}), "
                f"KeepInFlag={self.keep_in_flag}, KeepInCoord1={self.keep_in_coord1}, KeepInCoord2={self.keep_in_coord2}, "
                f"KeepOutFlag={self.keep_out_flag}, KeepOutCoord1={self.keep_out_coord1}, KeepOutCoord2={self.keep_out_coord2})")


# Example usage (for testing):
if __name__ == '__main__':
    # Create a command example:
    cmd = Commands(
        emergency_stop=True,
        autonomous_enabled=False,
        mission_lat=37.7749,
        mission_lon=-122.4194,
        keep_in_flag=1,
        keep_in_coord1=(37.7700, -122.4300),
        keep_in_coord2=(37.7800, -122.4100),
        keep_out_flag=0,  # no keep-out zone
        keep_out_coord1=(0.0, 0.0),
        keep_out_coord2=(0.0, 0.0)
    )
    encoded = cmd.encode()
    print("Encoded command (hex):", encoded.hex())
    decoded = Commands.decode(encoded)
    print("Decoded command:")
    print(decoded)
