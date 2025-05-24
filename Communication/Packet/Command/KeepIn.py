from Interfaces.CommandInterface import CommandInterface
import struct

class KeepIn(CommandInterface):
    PAYLOAD_ID = 1 # All commands will have a payload ID of 1
    COMMAND_ID = 2

    @staticmethod
    def encode_packet(coordinates) -> bytes:
        """Encode data packet

        Args:
            coordinates: List of (x, y) tuples to encode as doubles

        Returns:
            Encoded data bytes
        """
        # Start with payload and command IDs
        header = struct.pack("BB", KeepIn.PAYLOAD_ID, KeepIn.COMMAND_ID)
        # Flatten the list of tuples into a single list of floats
        flat_coords = [item for coord in coordinates for item in coord]
        print(f"Flat coords: {flat_coords}")
        # Build the format string: two bytes for header, then 2 doubles per coordinate
        format_string = f"{len(flat_coords)}d"
        if flat_coords:
            coords_bytes = struct.pack(format_string, *flat_coords)
            encoded_string = header + coords_bytes
        else:
            encoded_string = header
        return encoded_string

    @staticmethod
    def decode_packet(encoded_string) -> int:
        """Decodes data packet
        
        Args:
            encoded_string: Encoded data packet

        Returns:
            Data from encoded data packet
        """
        num_coordinates = (len(encoded_string) - 2) // 16
        if num_coordinates > 6:
            print("Too many coordinates")

        format_string = "=BB" + "dd" * int(num_coordinates)

        print(f"Format String: {format_string}")

        expected_length = struct.calcsize(format_string)
        if len(encoded_string) != expected_length:
            raise ValueError(f"Encoded string length {len(encoded_string)} does not match expected {expected_length} for format '{format_string}'")

        unpacked_data = struct.unpack(format_string, encoded_string)

        # Return an array of coordinates
        coords = unpacked_data[2:]
        return [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]