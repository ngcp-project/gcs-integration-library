from Commands import Commands_Vehicles
from Commands.Commands_Vehicles import CommandsRabbitMQ

vehicle = CommandsRabbitMQ("ERU")
def callback(channel, method, prop, body):
    print("Callback in Main received data from GCS")
    print(body)
try:
    vehicle.subscribe_all(callback)
except KeyboardInterrupt:
    print(" [*] Exiting. Closing connection.")
    vehicle.close_connection()
