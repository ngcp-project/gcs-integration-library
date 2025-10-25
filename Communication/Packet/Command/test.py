from EmergencyStop import EmergencyStop

print("Enabling Emergency Stop: ")

input = 0

encoded_data = EmergencyStop.encode_packet(input)

print(f"Expected string: '01 01 0{input}' Actual string: " + " ".join(f"{b:02x}" for b in encoded_data))

decoded_data = EmergencyStop.decode_packet(encoded_data)

print(decoded_data)