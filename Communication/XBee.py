import queue
import re   # Used to parse AT command lines from the config file
import serial   # Pyserial, used to cimmunicate over serial ports
import threading
import time     # Used for timeouts, sleep, and measuring performance

from Communication.interfaces.Serial import Serial  # Custom interface/base class for serial communication
from Communication.Frames import x81, x88, x89 # Frame parser for classes for each Xbee frame type
from Logger.Logger import Logger    # Custom logging class
from Communication.Frames import x81, x88, x89
from Logger.Logger import Logger
from Communication.tel_struct import Telemetry


TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

class XBee(Serial):
    # Configure serial port
    def __init__(self, port: str = None, baudrate: int = 115200, status: bool = False, logger: Logger = None, config_file: str = None):
        """Initialize serial connection

        Args:
          port: Port of serial device.
          baudrate: Baudrate of serial device (/port)
          status: Automatically receive status packets after a transmission.
          logger: Logger instance
        """
        self.port = port    # Serial port to use
        self.baudrate = baudrate     # Communication speed  
        self.ser = None      # Will hold the actual Serial object
        self.status = status     # If True, it will try to read back status frames (0x89)
        
        if logger is None:  
            self.logger = Logger()   # Create logger if not provided
            self.logger.write("LOGGER CREATED By XBee.py")
        else:
            self.logger = logger
        self.timeout = 0.05 # Allow programmer to configure timeout? # Max time to wait for responses
        self.frame_id = 0x01    # Frame ID (used to track commands)

        self.config_file = config_file # Add AT_Config.py file  # Path to config file with AT commands 

        # Retrieve Queues
        self.x81_queue: queue.Queue = queue.Queue()
        self.x88_queue: queue.Queue = queue.Queue() # If working properly, this queue should never have more than 1 element
        self.x89_queue: queue.Queue = queue.Queue()

        # Transmit Queue
        self.transmit_queue: queue.Queue = queue.Queue()

        # self.__transmitting = False # Flag: are we currently sending?
        # self.__receiving = False    # Flag: are we currently receiving?d1b2fd40841964d904a7927082

        self.logger.write(f"port: {self.port}, baudrate: {self.baudrate}, timeout: {self.timeout}, config_file: {self.config_file}")    # Log configuration for debugging
    

    def open(self):
        """Opens the serial port.

        Returns:
          True if success, False if failure (There is already an open port, close the port before opening another one).
        Raises:
          SerialException if there is an error opening the serial port
        """

        # Add try except blocks?
        def poll_and_write_serial():
            while self.ser is not None:
                # Check if there is a message to transmit
                if not self.transmit_queue.empty():
                    data = self.transmit_queue.get()
                    self.ser.write(data)
                # Check serial port for incomming data
                else:
                    self.__retrieve_data()
            else:
                # Normal exit of loop
                return 0
            



        self.logger.write("Attempting to open serial XBee connection.")

        if self.ser is not None:
            self.logger.write(f"A serial connection is already open. ser: {self.ser}")
            return False
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0) # Open the serial port
            self.logger.write("Serial port opened.")
            self.logger.write("Clearing input and output buffers.")

            self.ser.reset_input_buffer()   # Clear junk
            self.ser.reset_output_buffer()
            time.sleep(0.5)

            t1 = threading.Thread(target=poll_and_write_serial)
            t1.start()
        
            if self.config_file is not None:
                self.read_config(self.config_file)   # Optionally apply AT config
        
        except serial.SerialException as e:
            self.logger.write((f"Error opening serial port: {e}"))
            # print(f"Error opening serial port: {e}")
            raise serial.SerialException(e)

        return True

    def close(self):
        """Close serial port.

        Returns:
          True if success, False if failure (Error or port already closed).
        """
        if self.ser is not None:

            self.logger.write("Attempting to close serial XBee connection.")

            try:
                self.ser.close()    # Close the serial connection
                
                self.logger.write("Serial port closed.")

                self.ser = None # Reset to disconnected state 
            except Exception as e:
                self.logger.write(f"An error occured when closing serial port: {e}")
                raise Exception(e)
            return True
        self.logger.write("Serial port is already closed.")
        return False


    def transmit_data(self, data, address: str = "0000000000000000", retrieveStatus: bool = False):
        """Transmit data.
        Args:
          data: String data to transmit.
          address: Address of destination XBee module. "0000000000000000" if no value is provided.

        Returns:
          True if success, False if failure.
        """

        # Check if a serial port is open
        if self.ser is None:
            raise serial.SerialException("Error: Serial port is not open")
        
        if len(data) >= 100:
            self.logger.write(f"Error: Data should not exceed 100 bytes. Current size: {len(data)} bytes")
            raise Exception(f"Error: Data should not exceed 100 bytes. Current size: {len(data)} bytes")

        # self.__transmitting = True
        current_frame_id = self.frame_id
        self.logger.write(f"Transmitting data: {data} to {address}")

        encoded_data = self.__encode_data(data, address)
        self.transmit_queue.put(encoded_data) # Append encoded packet to transmit queue
        # self.ser.write(self.__encode_data(data, address))
        # self.__transmitting = False

        # If retrieve status is true
        if(retrieveStatus): # If caller wants TX status...
            # self.__receiving = True
            return self.__retrieve_transmit_status() # Wait for a 0x89 fram
        
        return False

    
    def __encode_data(self, data, address="0000000000000000"):
        frame = bytearray()
        frame.append(0x7E)  # Start delimiter
        data_length = len(data.encode('utf-8')) if isinstance(data, str) else len(data)
        frame.append(((data_length + 11) // 256))  # Length
        frame.append((data_length + 11) % 256)
        frame.append(0x00)  # Frame type
        frame.append(self.frame_id)
        self.frame_id = self.frame_id % 0xff + 0x01

        for i in range(8):
            frame.append(int(address[2 * i:2 * i + 2], 16))

        frame.append(0x00)  # Options
        if isinstance(data, str):
            frame.extend(data.encode('utf-8'))
        else:
            frame.extend(data)

        checksum = 0xFF - (sum(frame[3:]) & 0xFF)
        frame.append(checksum)

        self.logger.write("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))
        print("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))

        return frame


    def __retrieve_data(self):
        """
        Read incoming data in API mode:
        - Start delimiter (0x7E)
        - 2-byte Length
        - Frame Data (length bytes)
        - 1-byte Checksum

        Returns:
        - 0x81: (frame_type, source_address, rssi, options, data)
        - 0x88: (frame_type, frame_id, at_command, command_status, command_data)
        - 0x89: (frame_type, frame_id, status)
        """

        # Check if a serial port is open
        if self.ser is None:
            raise serial.SerialException("Error: Serial port is not open")

        # 1) Read one byte
        start_delim = self.ser.read(1)
        if not start_delim:
            # No data at all
            
            return None
    
        self.logger.write("Receiving data:")

        # 2) Check if it's 0x7E
        if start_delim[0] != 0x7E:
            # Not the start delimiter -> leftover byte from a second frame?
            print(f"Pass {start_delim[0]:02x}")
            self.logger.write(f"Pass {start_delim[0]:02x}", self.logger.WARNING)
            return None

        # 3) Read the next 2 bytes for length
        length_bytes = self.ser.read(2)
        if len(length_bytes) < 2:
            # Not enough data
            self.logger.write(f"Pass. Unable to read length bytes", self.logger.WARNING)
            return None

        length = (length_bytes[0] << 8) + length_bytes[1]
        # print("\nLength bytes:", f"{length_bytes[0]:02x}", f"{length_bytes[1]:02x}")
        # print("Length:", length)

        # 4) Read 'length' bytes of frame data
        frame_data = b''
        frame_data += self.ser.read(length)
        timeout_start = time.time()
        while len(frame_data) < length and time.time() < timeout_start + self.timeout:
            time.sleep(0.001)
            chunk = self.ser.read(length - len(frame_data))
            frame_data += chunk


        # print("Data Between Length & Checksum Fields:")
        # replacing the line bellow with logger.write
        # print(" ".join(f"{b:02x}" for b in frame_data))
        self.logger.write("Decoded frame data: "+ " ".join(f"{b:02x}" for b in frame_data))

        # 5) Read the 1-byte checksum
        checksum_raw = self.ser.read(1)
        # print("DEBUG: checksum_raw =", checksum_raw)

        if len(checksum_raw) < 1:
            # replacing print with logger write
            # print("DEBUG: No checksum byte read!")
            self.logger.write(f"DEBUG: No checksum byte read!", self.logger.WARNING)
            # Did not get the checksum byte
            return None

        expected_checksum = checksum_raw[0]

        # 6) Calculate & print checksums
        calculated_checksum = 0xFF - (sum(frame_data) & 0xFF)
        # Replace these print() with logger.write
        #print("Received Checksum:", f"{expected_checksum:02x}")
        #print("Calculated Checksum:", f"{calculated_checksum:02x}")
        
        self.logger.write(f"Received Checksum: {expected_checksum:02x}", self.logger.DEBUG)
        self.logger.write(f"Calculated Checksum: {calculated_checksum:02x}", self.logger.DEBUG)
        
        # 7) Compare checksums
        if expected_checksum != calculated_checksum:
            # Replacing with logger.write too
            # print("Checksum mismatch - ignoring frame.")
            self.logger.write("Checksum mismatch - ignoring frame.", self.logger.WARNING)
            self.logger.write(f"Checksum mismatch - ignoring frame: {frame_data} expected: {expected_checksum} received: {calculated_checksum}", self.logger.WARNING)
            return None

        # 8) Now parse the frame
        #    The first byte of frame_data is the frame_type
        frame_type = frame_data[0]
        if frame_type == 0x81:
            self.logger.write("Adding frame to 0x81 (Rx Packet) queue")
            frame: x81 = self.__0x81(frame_data)
            self.x81_queue.put(frame)
            return frame
        
        elif frame_type == 0x88:
            self.logger.write("Adding frame to 0x88 (AT Command Response) queue")
            frame: x88 = self.__0x88(frame_data)
            self.x88_queue.put(frame)
            return frame
        
        elif frame_type == 0x89:
            self.logger.write("Adding frame to 0x89 (Tx Status) queue")
            frame: x89 = self.__0x89(frame_data)
            self.x89_queue.put(frame)
            return frame
        
        else:
            # For all other frame types, just ignore or print a debug
            self.logger.write(f"Pass. Unhandled frame type: {frame_data}", self.logger.ERROR)
            print(f"Got frame type: 0x{frame_type:02X}, ignoring.")
            return None

    def retrieve_data(self) -> x81:
        """
        Retrieves one frame of data (0x81 - Rx Packet)

        Returns:
        - 0x81: (frame_type, source_address, rssi, options, data)
        - None: If there is no data.
        """

        # if not self.x81_queue.empty():
            # return self.x81_queue.get(True, self.timeout)
        # else:
            # return None
        try:
            data = self.x81_queue.get(True, self.timeout)
        except:
            return None
        else:
            return data
        
    def __retrieve_at_command_response(self) -> x88:
        """
        Retrieves one AT response frame (0x88 - Rx Packet)

        Returns:
        - 0x88: (frame_type, frame_id, at_command, status, data)
        - None: If there is no data.
        """
        # if not self.x88_queue.empty():
        #     return self.x88_queue.get()
        # else:
        #     return None
        
        try:
            data = self.x88_queue.get(True, self.timeout)
        except:
            return None
        else:
            return data
        
    def __retrieve_transmit_status(self) -> x89:
        """
        Retrieves one transmit status frame (0x89 - Tx Status)

        Returns:
        - 0x89: (frame_type, frame_id, status)
        - None: If there is no data.
        """
        # if not self.x89_queue.empty():
        #     return self.x89_queue.get()
        # else:
        #     return None

        try:
            data = self.x89_queue.get(True, self.timeout)
        except:
            return None
        else:
            return data
    

    # # NOTE** Might need to check data length
    # def __encode_data(self, data, address = "0000000000000000"):
    #     """Encode String data.

    #     Args: 
    #       data: String data to encode.
    #       address: Address of destination XBee module. "0000000000000000" if no value is provided.
    #     Returns:
    #       Framed String data.
    #     """
    #     frame = bytearray()
    #     frame.append(0x7E)  # Start delimiter (1 byte)
    #     frame.append(((len(data) + 11) // 256))  # Length (2 bytes)
    #     frame.append((len(data) + 11) % 256)
    #     frame.append(0x00)  # Frame type (1 byte)
    #     frame.append(self.frame_id)  # Frame ID (1 bytes)
    #     self.frame_id = self.frame_id % 0xff + 0x01

    #     for i in range(8):  # 64-bit address (8 bytes)
    #         frame.append(int(address[2 * i : 2 * i + 2], 16))

    #     frame.append(0x00)  # Options (1 byte)
    #     frame.extend(data.encode('utf-8'))  # RF data (0 - 256 bytes)
    #     # FF - number of bytes between length & checksum field
    #     checksum = 0xFF - (sum(frame[3:]) & 0xFF)
    #     frame.append(checksum)  # Checksum (1 byte)

    #     # print(frame)
    #     # print("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))
    #     self.logger.write("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))

    #     return frame
    
    def request_at_command_data(self, id, retry = 3) -> x88:

        # Check if a serial port is open
        if self.ser is None:
            raise serial.SerialException("Error: Serial port is not open")
        
        if id == None:
            return None
        
        current_frame_id = self.frame_id
        self.frame_id = self.frame_id % 0xff + 0x01

        frame = bytearray()
        frame.append(0x7E) # Start delimiter (1 byte)
        frame.append(0x00) # Length (2 bytes)
        frame.append(0x04) # Length
        frame.append(0x08) # Frame Type (1 byte)
        frame.append(current_frame_id) # Frame ID (1 byte)
        frame.extend(id.encode('utf-8')) # AT command (2 bytes)
        checksum = 0xFF - (sum(frame[3:]) & 0xFF)
        frame.append(checksum)  # Checksum (1 byte)

        print("Sending: " + ''.join('{:02x} '.format(x) for x in frame))
        self.logger.write("Sending: " + ''.join('{:02x} '.format(x) for x in frame))

        # self.ser.write(frame)
        self.transmit_queue.put(frame)

        # timeout_start = time.time()
        # while time.time() < timeout_start + self.timeout:
        #     time.sleep(0.001)
        #     response: x88 = self.retrieve_data()

        #     if response is not None and response.frame_type == 0x88:
        #         self.logger.write(f"Response: {response}")
        #         return response
        response: x88 = self.__retrieve_at_command_response()
        
        # Correct response received
        if response is not None and response.frame_id == current_frame_id:
            return response

        # No response or incorrect response received
        if ((response is None) or (response is not None and response.frame_id != current_frame_id)) and retry > 0:
            # Clear queue just in case
            with self.x88_queue.mutex:
                self.x88_queue.queue.clear()
            self.logger.write(f"No response when running At Command {id}. Retries remaining: {retry}")
            return self.request_at_command_data(id, (retry - 1))

        self.logger.write(f"No response when running AT Command {id}")
        return None

    def __0x81(self, frame_data) -> x81:
        """Handle XBee Frame Type 81 (Frame Receive: 16-bit Address)

        Args:
          frame_data: Received bytes (between length and checksum fields)

        Returns:
          xxxxDecoded message & Received Signal Strength Indicator (RSSI), None if there is an error decoding message
          Returns 0x81 class (frame_type, frame_id, payload, rssi, ...)
        """
        frame_type = frame_data[0]
        source_address = frame_data[1:3]
        rssi = -frame_data[3]
        options = frame_data[4]
        data = frame_data[5:]
        try:
            if data[0] == TAG_TELEMETRY:
                decoded_message = Telemetry.decode(data[1:])  # ← Skip tag byte
            else:
                decoded_message = data.decode(errors="ignore")  # fallback

            self.logger.write(f"Received payload. RSSI: {rssi}, Decoded message: {decoded_message}")
            
            #print(f"RSSI (Signal Strength : {rssi} dBm)")
            #print("Decoded message:", decoded_message)
               
            frame = x81(frame_type, source_address, rssi, options, decoded_message)
            self.logger.write(f"[Frame Receive: 16-bit Address] Frame Type: {frame.frame_type}, Source Address: {frame.source_address}, RSSI: {frame.rssi}, Options: {frame.options}, Data: {frame_data}")
            return frame
        except UnicodeDecodeError:
            self.logger.write(f"Error decoding payload. RSSI: {rssi}, Decoded message: {decoded_message}")
            print("Error decoding payload")
            return None
        
    def __0x88(self, frame_data) -> x88:
        """Handle XBee Frame Type 88 (AT Command Response)

        Args:
          frame_data: Received bytes (between length and checksum fields)

        Returns:
          Returns 0x88 class (frame_type, frame_id, at_command, command_status_ command_data)
        """
        # print(" ".join(f"{b:02x}" for b in frame_data))
        # print(frame_data)
        frame_type = frame_data[0]
        frame_id = frame_data[1]
        at_command = frame_data[2:4]
        command_status = frame_data[4]
        command_data = frame_data[5:]
        frame = x88(frame_type, frame_id, at_command, command_status, command_data)
        self.logger.write(f"[AT Command Response] Frame Type: {frame.frame_type}, Frame ID: {frame.frame_id}, AT Command: {frame.at_command}, Command Status: {frame.status}, Command Data: {frame.data}")
        return frame

    def __0x89(self, frame_data) -> x89:
        """Handle XBee Frame Type 89 (Transmit Status)

        Args:
          frame_data: Received bytes (between length and checksum fields)

        Returns:
          Returns 0x89 class (frame_type, frame_id, delivery_status)
        """
        frame_type = frame_data[0]
        frame_id = frame_data[1]
        delivery_status = frame_data[2]
        frame: x89 = x89(frame_type, frame_id, delivery_status)

        self.logger.write(f"[Transmit status] Frame Type: {frame.frame_type}, Frame ID: {frame.frame_id}, Status: {frame.status}")
        return frame
    
    def read_config(self, filename):
        """
        Reads AT Commands from a file and logs their execution.

        Args:
          filename: Filename of file with a list of AT commands to execute.
        """

        # Check if a serial port is open
        if self.ser is None:
            raise serial.SerialException("Error: Serial port is not open")

        with open(filename, 'r') as file:
            lines = file.readlines()
        
        current_category = ""
        start_time = time.time()

        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                if line.startswith("#"):
                    current_category = line[1:].strip()
                    # print(f"\n{current_category}")
                    self.logger.write(f"\n{current_category}")
                continue
            
            # Subcategories (##)
            if line.startswith("##"):
                current_category = line[2:].strip()
                # print(f"\n{current_category}")
                self.logger.write(f"\n{current_category}")
                continue
            
            # Match AT Commands (handling special characters like % and ?)
            match = re.match(r"\*\s+([%A-Za-z0-9?]+)\s+-\s+(.+)", line)
            if match:
                at_command_id, command_name = match.groups()
                self.logger.write(f"Requesting: {at_command_id}")
                response = self.request_at_command_data(at_command_id)
                
                if response:
                    # if at_command_id
                    log_entry = f"{response}"
                    # print(f"Response: {log_entry}")
                    # self.logger.write(f"Response: {log_entry}")
                # else:
                    # print("No response")
                    # self.logger.write("No Response")
        end_time = time.time()
        self.logger.write(f"Retrieved config in: {end_time - start_time}s")
