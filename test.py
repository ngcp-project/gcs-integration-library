from Commands.RabbitMQ import CommandsRabbitMQ
from Types.CommandsEnum import CommandsEnum

def main():
    vehicle = CommandsRabbitMQ("ERU")
    def callback(channel, method, prop, body):
        pass
    try:
        # Subscribing to a specific command (e.g., MANUAL_MODE)
        vehicle.subscribe(CommandsEnum.TARGET.value, callback)
        # vehicle.subscribe_all(callback)
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()
# Executing the main function
if __name__ == "__main__":
    main()