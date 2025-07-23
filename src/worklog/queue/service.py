import pika
import json

class RabbitMQPublisher:
    def __init__(self, host='rabbitmq', queue='chat_queue', user='user', password='password'):
        self.queue = queue
        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(host=host, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def send(self, payload: dict):
        body = json.dumps(payload).encode()
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=body
        )
        print(f"📤 Sent: {payload}")
