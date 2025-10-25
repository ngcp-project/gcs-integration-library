# Can be used to implement the serial port manager for other radio modules

class CommandInterface:
    # FORMAT_STRING = # More information here: https://docs.python.org/3/library/struct.html
    PAYLOAD_ID = 1 # All commands will have a payload ID of 1
    # COMMAND_ID =

    @staticmethod
    def encode_data(data) -> str:
        """Encode data packet

        Args:
          data: Data passed into given command

        Returns:
          Encoded data string
        """
        pass

    @staticmethod
    def decode_data(encoded_string) -> str:
        """Decodes data packet
        
        Args:
          Encoded data packet

        Returns:
          Data from encoded data packet
        """
        pass