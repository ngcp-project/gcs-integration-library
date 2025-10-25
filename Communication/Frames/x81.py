# from Communication.XBee.Frames import FrameInterface
class x81():
    def __init__(self, frame_type, source_address, rssi, options: int, data: str):
        self.frame_type = frame_type
        self.source_address = source_address
        self.rssi = rssi
        self.options = options
        self.data = data
