import pika 

connection = pika.BlockingConnection(pika.ConnectionParameters(host="192.168.0.101"))
channel=connection.channel()
vehicleName = "eru"
channel.queue_declare(queue=f"telemetry_{vehicleName}")
channel.basic_publish(exchange='', routing_key=f"telemetry_{vehicleName}", body='working now?')
print("did send it")
connection.close()