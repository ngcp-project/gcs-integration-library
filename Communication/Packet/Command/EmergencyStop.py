from Interfaces.CommandInterface import CommandInterface
import struct

class EmergencyStop(CommandInterface):
    FORMAT_STRING = "BBB"
    PAYLOAD_ID = 1 # All commands will have a payload ID of 1
    COMMAND_ID = 1

    @staticmethod
    def encode_packet(stop_status) -> bytes:
        """Encode data packet

        Args:
            stop_status: Status for emergency stop: 0 = Enable Emergency Stop, 1 = Disable Emergency Stop

        Returns:
            Encoded data bytes
        """
        encoded_string = struct.pack(EmergencyStop.FORMAT_STRING, EmergencyStop.PAYLOAD_ID, EmergencyStop.COMMAND_ID, stop_status)
        return encoded_string

    @staticmethod
    def decode_packet(encoded_string) -> int:
        """Decodes data packet
        
        Args:
            encoded_string: Encoded data packet

        Returns:
            Data from encoded data packet
        """
        expected_size = 3
        if len(encoded_string) != expected_size:
            print("Invalid String Size")
        unpacked_data = struct.unpack(EmergencyStop.FORMAT_STRING, encoded_string)

        return unpacked_data[2]
