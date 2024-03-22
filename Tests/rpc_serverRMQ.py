# Vehicle
import pika 
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel(0)

channel.queue_declare(queue='rpc_queue')

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        time.sleep(7)
        return "Got It :D"

# Callback for basic consume
# 
def on_request(ch, method, props, body):
    
    n = int(body)
    
    # print(f" [.] fib({n})")
    print("[.] Vehicle received commands from GCS")
    response = fib(n)
    
    ch.basic_publish(exchange='', routing_key=props.reply_to, 
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    last_call = time.time()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting GCS RPC requests")
channel.start_consuming()
