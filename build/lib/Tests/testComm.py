from Types.Commands import Commands  # Make sure to import your Commands class
from Types.Geolocation import Coordinate, Polygon

# Import your CommandsRabbitMQ class with the modifications provided earlier
from Commands.CommandsSub import CommandsRabbitMQ  

def main():
    vehicle_name = 'ERU'
    binding_key = 'commands'
    coordinate = Coordinate(latitude=12.48388, longitude=133.293292)
    coordinate_list = [Coordinate(12.999, 211.33), Coordinate(23, 22)]
    polygon = Polygon
    # Instantiate CommandsRabbitMQ
    commands_rabbitmq = CommandsRabbitMQ(vehicle_name, binding_key)

    try:
        # Subscribe to all commands
        commands_rabbitmq.subscribe_all()

        # Simulate sending a command
        command_data = Commands(isManual=1, target=coordinate, searchArea=coordinate_list)
        # print(command_data.to_dict())

    except KeyboardInterrupt:
        print("Exiting. Closing connection.")
        commands_rabbitmq.close_connection()

