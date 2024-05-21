# GCS Vehicle Integration Library
Make sure to do `pip install pika` to be able to run this library

If you are on Powershell, set up the python environment by: 

**Check Dependencies:**

*  make sure you have RabbitMQ installed: [Install RabbitMQ](https://www.rabbitmq.com/download.html)

**Before running your code**
* Make sure you are at the root dir.
* Open a powershell terminal within VSCode and use the command `python -m venv .venv` to create a virtual environment. 
* To activate, run this command `.\venv\Scripts\Activate.ps1`
* If that command give you errors, run this command instead:
`.\venv\Scripts\activate.bat`
* Set up your python path: `$env:PYTHONPATH = "$PWD"` (trouble-shooting)
* To check if your PYTHONPATH has been set up correctly, run this command: `echo $PYTHONPATH` and it should prints your current home directory path. 
* **Run Docker container** using this command: `docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management`

### For Vehicle to Subscribe to Commands from the GCS
**Subscribe to ALL Commands**
* In your folder, make sure to follow this template: (e.g test.py)
```
from Commands.Commands_Vehicles import CommandsRabbitMQ
from Types.CommandsEnum import CommandsEnum

def main():
  # Choose your vehicle name, ERU is used as an example
    vehicle = CommandsRabbitMQ("ERU")

    def callback(channel, method, prop, body):
        pass
    try:
        # Subscribing to all commands
        vehicle.subscribe_all(callback)
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()
# Executing the main function
if __name__ == "__main__":
    main()
```

**Subscribe to one command at a time**
* In your folder, make sure to follow this template: (e.g test.py)
```
from Commands.Commands_Vehicles import CommandsRabbitMQ
from Types.CommandsEnum import CommandsEnum

def main():
  # Choose your vehicle name, ERU is used as an example
    vehicle = CommandsRabbitMQ("ERU")

    def callback(channel, method, prop, body):
        pass
    try:
        # Subscribing to one command. (e.g Target Coordinate)
        vehicle.subscribe(CommandsEnum.TARGET.value, callback)
    except KeyboardInterrupt:
        print(" [*] Exiting. Closing connection.")
        vehicle.close_connection()
# Executing the main function
if __name__ == "__main__":
    main()
```

#### In the GCS side, data is passed as the below: (e.g is from Commands/Commands_GCS.py)
```
coordinates_01 = Coordinate(latitude = 35.35, longitude =  60.35)

coordinates_02 = Coordinate(latitude = 40.35, longitude =  50.35)
coordinates_03 = Coordinate(latitude = 44.35, longitude =  55.35)
search_area_coordinates = [coordinates_02, coordinates_03]

search_area_list = Polygon(coordinates =  search_area_coordinates)

data = Commands( 
    isManual=True,
    target=coordinates_01,
    searchArea=search_area_list
)
```

****
To set up docker: Dowload Docker Laptop: [Get Started with Docker](https://www.docker.com/get-started/)

Create python library 
python setup.py