# Vehicle
import pika 
import time
import json
from Types.Commands import Commands
from Types.Geolocation import Coordinate, Polygon

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel(0)

channel.queue_declare(queue='rpc_queue')

def isManual(isManual:bool):
    print(f"Manual is:{isManual}")
    
def target(target:Coordinate):
    print(f"Target Coordinate is:{target}")
    
def searchArea(searchArea:Polygon):
    print(f"Search Area is:{searchArea}")
    
def subscribe_all(commands_data) -> str:
    command_dict = json.loads(commands_data)
    
    is_manual = command_dict['isManual']
    target_latitude = command_dict['target']['latitude']
    target_longitude = command_dict['target']['longitude']
    
    
    # searchArea_latitude = command_dict['searchArea']['latitude']
    # searchArea_longitude = command_dict['searchArea']['longitude']
    search_area_coordinates = command_dict['searchArea']['coordinates']
    search_area_coordinates_list = []
    for coor_dict in search_area_coordinates:
        search_area_latitude = coor_dict['latitude']
        search_area_longitude = coor_dict['longitude']
        search_area_coordinates_list.append(Coordinate(latitude=search_area_latitude, longitude=search_area_longitude))
        
    
    targetCoordinate = Coordinate(target_latitude, target_longitude)
    search_area = Polygon(coordinates=search_area_coordinates_list)
    isManual(is_manual)
    target(targetCoordinate)
    searchArea(search_area)
    
    return f"[.] Vehicle received commands from GCS and Answer: {commands_data}"

def on_request(ch, method, props, body):
    
    commands = body
    
    response = subscribe_all(commands)
    # print(f"[.] Vehicle received commands from GCS: {commands}")
    
    ch.basic_publish(exchange='', routing_key=props.reply_to, 
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    last_call = time.time()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
print(" [x] Awaiting GCS RPC requests")
channel.start_consuming()
