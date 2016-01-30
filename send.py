#!/usr/bin/env python
import pika
from connection import *

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue=queue)

channel.basic_publish(exchange='', routing_key=queue, body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
