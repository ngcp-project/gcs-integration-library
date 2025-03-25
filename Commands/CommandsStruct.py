import struct

class Commands:
    """
    Handles command data encoding and decoding for vehicle commands.
    
    The binary packet structure is defined as follows (85 bytes total):
      Format: "=B2B2dB4dB4d"
      
      Breakdown:
        - B: Vehicle ID (1 byte) — a numeric code (e.g., 0x01 for ERU)
        - 2B: emergency_stop, autonomous_enabled (1 byte each, converted to 0 or 1)
        - 2d: mission_lat, mission_lon (each double, 8 bytes each, 16 bytes total)
        - B: keep_in_flag (1 byte)
        - 4d: keep_in coordinates (4 doubles, 32 bytes total) — two coordinate pairs
        - B: keep_out_flag (1 byte)
        - 4d: keep_out coordinates (4 doubles, 32 bytes total)
    """
    def __init__(self, vehicle_id, emergency_stop, autonomous_enabled, mission_lat, mission_lon,
                 keep_in_flag, keep_in_coord1, keep_in_coord2,
                 keep_out_flag, keep_out_coord1, keep_out_coord2):
        self.vehicle_id = vehicle_id                    # int (0-255)
        self.emergency_stop = emergency_stop            # bool
        self.autonomous_enabled = autonomous_enabled    # bool
        self.mission_lat = mission_lat                  # float
        self.mission_lon = mission_lon                  # float
        self.keep_in_flag = keep_in_flag                # bool/int (0 or 1)
        self.keep_in_coord1 = keep_in_coord1            # tuple of (lat, lon)
        self.keep_in_coord2 = keep_in_coord2            # tuple of (lat, lon)
        self.keep_out_flag = keep_out_flag              # bool/int (0 or 1)
        self.keep_out_coord1 = keep_out_coord1          # tuple of (lat, lon)
        self.keep_out_coord2 = keep_out_coord2          # tuple of (lat, lon)
    
    def encode(self):
        """
        Encodes the command data into an 85-byte binary packet.
        """
        format_string = "=B2B2dB4dB4d"
        # Convert booleans to integers (0 or 1)
        vid = self.vehicle_id
        es = 1 if self.emergency_stop else 0
        ae = 1 if self.autonomous_enabled else 0
        kin = 1 if self.keep_in_flag else 0
        kout = 1 if self.keep_out_flag else 0
        # Pack keep_in coordinates: two pairs (4 doubles)
        kin_values = (self.keep_in_coord1[0], self.keep_in_coord1[1],
                      self.keep_in_coord2[0], self.keep_in_coord2[1])
        # Pack keep_out coordinates: two pairs (4 doubles)
        kout_values = (self.keep_out_coord1[0], self.keep_out_coord1[1],
                       self.keep_out_coord2[0], self.keep_out_coord2[1])
        return struct.pack(format_string,
                           vid,            # Vehicle ID (1 byte)
                           es, ae,         # emergency_stop, autonomous_enabled (2 bytes)
                           self.mission_lat, self.mission_lon,   # Mission coordinates (16 bytes)
                           kin,          # keep_in_flag (1 byte)
                           *kin_values,  # 4 doubles (32 bytes)
                           kout,         # keep_out_flag (1 byte)
                           *kout_values) # 4 doubles (32 bytes)
    
    @staticmethod
    def decode(binary_data):
        """
        Decodes an 85-byte binary packet into a Commands object.
        """
        format_string = "=B2B2dB4dB4d"
        expected_size = struct.calcsize(format_string)
        if len(binary_data) != expected_size:
            print(f"Invalid command packet size. Expected {expected_size}, got {len(binary_data)}")
            return None
        unpacked = struct.unpack(format_string, binary_data)
        vid = unpacked[0]
        es = unpacked[1]
        ae = unpacked[2]
        mlat = unpacked[3]
        mlon = unpacked[4]
        kin_flag = unpacked[5]
        kin_vals = unpacked[6:10]
        kout_flag = unpacked[10]
        kout_vals = unpacked[11:15]
        kin_coord1 = (kin_vals[0], kin_vals[1])
        kin_coord2 = (kin_vals[2], kin_vals[3])
        kout_coord1 = (kout_vals[0], kout_vals[1])
        kout_coord2 = (kout_vals[2], kout_vals[3])
        return Commands(vid, bool(es), bool(ae), mlat, mlon,
                        kin_flag, kin_coord1, kin_coord2,
                        kout_flag, kout_coord1, kout_coord2)
    
    def __str__(self):
        return (f"Commands(Vehicle ID={self.vehicle_id}, EmergencyStop={self.emergency_stop}, "
                f"AutonomousEnabled={self.autonomous_enabled}, Mission=({self.mission_lat}, {self.mission_lon}), "
                f"KeepInFlag={self.keep_in_flag}, KeepInCoord1={self.keep_in_coord1}, KeepInCoord2={self.keep_in_coord2}, "
                f"KeepOutFlag={self.keep_out_flag}, KeepOutCoord1={self.keep_out_coord1}, KeepOutCoord2={self.keep_out_coord2})")
