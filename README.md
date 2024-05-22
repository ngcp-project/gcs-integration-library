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
**Subscribe to one command at a time**
* In your folder, make sure to follow this template: (e.g test.py). In this example, the vehicle ERU is subscribing to the Manual Mode command from the GCS.
```
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
# Executing the main function
if __name__ == "__main__":
    main()
```

#### In the GCS side, data is passed as the below: (e.g is from Commands/Commands_GCS.py)
```
gcs_rpc = GCSRabbitMQ()

print(" [x] Start sending commands to Vehicles")
coordinates_01 = Coordinate(latitude=35.35, longitude=60.35)
coordinates_02 = Coordinate(latitude=40.35, longitude=50.35)
coordinates_03 = Coordinate(latitude=44.35, longitude=55.35)
search_area_coordinates = [coordinates_02, coordinates_03]
search_area_list = Polygon(coordinates=search_area_coordinates)

coordinates_04 = Coordinate(latitude=40.35, longitude=50.35)
coordinates_05 = Coordinate(latitude=44.35, longitude=55.35)
keep_in_coordinates = [coordinates_04, coordinates_05]
keep_in_list = Polygon(coordinates=keep_in_coordinates)

coordinates_06 = Coordinate(latitude=40.35, longitude=50.35)
coordinates_07 = Coordinate(latitude=44.35, longitude=55.35)
keep_out_coordinates = [coordinates_06, coordinates_07]
keep_out_list = Polygon(coordinates=keep_out_coordinates)

data_eru = Commands(
    isManual=True,
    emergencyStop=False,
    target=coordinates_01,
    searchArea=search_area_list,
    keepIn=keep_in_list,
    keepOut=keep_out_list
)

command_type = CommandsEnum.MANUAL_MODE
response_eru = gcs_rpc.call("eru", command_type, data_eru)
print(f"Command is: {data_eru.isManual}")
print(f"Response from ERU: {response_eru}")
```
* If the command is Keep_In or Keep_Out, all the vehicles that are available on the scene will be subscribing to the same command.
```
command_type = CommandsEnum.KEEP_IN

 ### For Keep_In, Keep_Out Zone:
if command_type == CommandsEnum.KEEP_IN:
    for vehicle_name in vehicles_list:
        gcs_rpc_vehicle = GCSRabbitMQ(vehicle_name)
        response = gcs_rpc_vehicle.call(vehicle_name, command_type, data)
        print(f"\nResponse from {vehicle_name.upper()}: {response}")
```

****
To set up docker: Dowload Docker Laptop: [Get Started with Docker](https://www.docker.com/get-started/)

Create python library 
python setup.py