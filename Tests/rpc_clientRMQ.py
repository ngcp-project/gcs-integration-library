# GCS
#!/usr/bin/env python
import pika
import uuid
import time

flag_count =0

class FibonacciRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    # Basically a callback function
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        global last_call
        global flag_count
        flag_count = 0
        last_call = time.time()
        
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        
        while self.response is None:  
            self.connection.process_data_events(time_limit=3)
            if time.time() - last_call > 3:  # Check if 3 seconds have elapsed
                flag_count += 1
                print(f"Flag(s) raised: {flag_count}")
                last_call = time.time()
                if flag_count == 3:
                    print("[x] Vehicle is missing [x]")
                    return "Vehicle is missing"

        return str(self.response)


fibonacci_rpc = FibonacciRpcClient()

print(" [x] Sending commands to Vehicles")
response = fibonacci_rpc.call(30)
print("Response:", response)


    

