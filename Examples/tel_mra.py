from Telemetry.RabbitMQ import TelemetryRabbitMQ
from Types.Telemetry import Telemetry
from Types.Geolocation import Coordinate
import socket, random, datetime

vehicle = TelemetryRabbitMQ("MRA", "localhost")
deviceIp = socket.gethostbyname(socket.gethostname())
longitude = -120.752837
latitude = 35.328485
altitude = 0
batteryLife = 1

yaw = 0
pitch = 0
roll = 0
speed = 0

fireCoordinate = Coordinate(latitude=latitude+0.00002,longitude=longitude-0.00002)

tel = Telemetry(
    localIP=deviceIp,
    pitch=pitch,
    yaw=yaw,
    roll=roll,
    currentPosition=Coordinate(latitude=latitude,longitude=longitude),
    altitude=altitude,
    batteryLife=batteryLife,
    vehicleStatus="In Use",
    fireFound=False,
    fireCoordinate=fireCoordinate,
    vehicleSearch=fireCoordinate,
    speed=speed,
    lastUpdated=datetime.datetime.now()
)

def randPM(i: int): return -1*i if random.randint(0,1) else i
def randPMAbsolute(i: int): return -1*i if (random.randint(0,1) and altitude-(i*-1) > 0) else i

loop_counter = 10000


if __name__ == '__main__':
    try:
        while True:
            vehicle.publish(data=tel)
            loop_counter -= 1

            tel.currentPosition.longitude += randPM(0.000002)
            tel.currentPosition.latitude += randPM(0.000001)
            tel.yaw += randPM(0.01)
            tel.pitch += randPM(0.01)
            tel.roll += randPM(0.01)

            tel.altitude += randPMAbsolute(0.01)
            tel.speed += randPMAbsolute(1)
            tel.batteryLife -= 0.0001*random.randint(0,1)

            if loop_counter < 0 and loop_counter > -100: 
                tel.fireFound = True
                tel.fireCoordinate.longitude += randPM(0.000002)
                tel.fireCoordinate.latitude += randPM(0.000001)
                tel.vehicleSearch.longitude += randPM(0.000002)
                tel.vehicleSearch.latitude += randPM(0.000001)

    except Exception as e:
        print(e)
        vehicle.close_connection()

