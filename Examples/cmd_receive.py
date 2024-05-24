from Commands.RabbitMQ import CommandsRabbitMQ
from Types.CommandsEnum import CommandsEnum

vehicle = CommandsRabbitMQ("ERU")

def callback_target(body):
    print("Target received from GCS!")
    print(body)

def callback_search(body):
    print("Search Area received from GCS!")
    print(body)

def callback_manual(body):
    print("Manual Mode Update received from GCS!")
    print(body)

try:
    vehicle.subscribe(CommandsEnum.TARGET, callback_target)
    vehicle.subscribe(CommandsEnum.SEARCH_AREA, callback_search)
    vehicle.subscribe(CommandsEnum.MANUAL_MODE, callback_manual)
    
    vehicle.start_connection()

except KeyboardInterrupt:
    print("[*] Exiting...")
    vehicle.close_connection()
    

