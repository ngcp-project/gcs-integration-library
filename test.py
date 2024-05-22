from Commands.RabbitMQ import CommandsRabbitMQ
from Types.CommandsEnum import CommandsEnum

def main() :
    # vehicleName = input("Enter vehicle name: ").strip()
    vehicleName = "eru"
    command_name = CommandsEnum.MANUAL_MODE
    vehicle = CommandsRabbitMQ(vehicleName, command_name)
    
    print("Vehicle side")
    
    def callback(channel, method, prop, body):
        pass
    try:
        vehicle.subscribe(command_name, vehicleName, CommandsEnum.MANUAL_MODE.value, callback)
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()
