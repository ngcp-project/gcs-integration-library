from Interfaces.CommandInterface import CommandInterface
import struct

class CommandResponse(CommandInterface):
    FORMAT_STRING = "BBB"
    PAYLOAD_ID = 1 # All commands will have a payload ID of 1
    COMMAND_ID = 0

    @staticmethod
    def encode_packet(commandId) -> str: # Maybe pass the packet back
        """Encode data packet

        Args:
            stop_status: Status for emergency stop: 0 = Enable Emergency Stop, 1 = Disable Emergency Stop

        Returns:
            Encoded data string
        """
        encoded_string = struct.pack(CommandResponse.FORMAT_STRING, CommandResponse.PAYLOAD_ID, CommandResponse.COMMAND_ID, commandId)
        return encoded_string

    @staticmethod
    def decode_packet(encoded_string) -> str:
        """Decodes data packet
        
        Args:
            Encoded data packet

        Returns:
            Data from encoded data packet
        """
        expected_size = 3
        if len(encoded_string) != expected_size:
            print("Invalid String Size")
        unpacked_data = struct.unpack(CommandResponse.FORMAT_STRING, encoded_string)

        return unpacked_data[2]
