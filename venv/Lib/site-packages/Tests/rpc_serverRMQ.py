import pika 
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel(0)

channel.queue_declare(queue='rpc_queue')
last_call = time.time()
flag_count = 0

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

# Callback for basic consume
# 
def on_request(ch, method, props, body):
    global last_call
    global flag_count
    flag_count = 0
    
    n = int(body)
    
    print(f" [.] fib({n})")
    response = fib(n)
    
    ch.basic_publish(exchange='', routing_key=props.reply_to, 
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    last_call = time.time()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
try:
    while True:
        connection.process_data_events()
        #channel.start_consuming()
        if time.time() - last_call > 4:
            flag_count += 1
            print(f"not receiving calls, raised flag(s): {flag_count}")
            last_call = time.time()
            if flag_count == 3:
                print("!!!!time out!!!!")
                connection.close()
                break
        time.sleep(1)
except KeyboardInterrupt:
    print(" [x] Server cancelled by user")
    connection.close()