# GCS Vehicle Integration Library

# Instructions for using NATS:  

## Requirements
- Downloading The NATS Image Here: https://hub.docker.com/_/nats and running the container  
- You must also run a Python venv with Python version **3.10.0**  
- You may also need to run "pip install nats-py" in case the package is not converted to the virtual environment correctly  
- To use the C# imports, you need to include the file INSIDE OF the C# project.


## **__Telemetry__** 
   
### *Python (Publisher)*  

**Class Initalization**  
- NATS_Pub.TelemetryNATS() 
  - Used for initialzing the Publisher System

**Functions**  
- setup_NATS(node_name, ipv4)  
  - node_name (String): Name of the publisher you are publishing to (ex: "uav")
  - ipv4 (String): ipv4 address of the computer **<u>you are sending TO</u>** (the subscriber, not the computer you are running the python script on) (Ex: "192.168.1.100")

- publish_NATS(tel)
  - tel (Telemetry from Types): Telemtery object from the types directory  
    (Ex:  
    tel = Telemetry.Telemetry(  
    pitch=6.0,  
    yaw=0.2,  
    roll=1.2,  
    speed=1.0,  
    altitude=5.0,  
    batteryLife=1.2,  
    currentCoordinate=Coordinate(  
        latitude=30,  
        longitude=60  
    ),
    vehicleStatus=Telemetry.Status.IN_USE,  
    lastUpdated=datetime.now())  
    )

### *C# (.net) (Subscriber)*  

**Class Initalization/Functions**  
- TelemetryNATS.setup_NATS(node_name)  
  - node_name (String): Name of the subscriber you are subscribing to. Must be the same name as the publisher (ex: "uav")
  - Returns the telemetry object as a json in String format

