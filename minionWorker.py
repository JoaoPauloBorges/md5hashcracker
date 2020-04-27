#!/usr/bin/env python
import pika
import json
import uuid
from minion import minion


def fetcher(resp):
    import requests

    req = requests.get(resp['url'])
    out = minion(resp['hash'], req.text, True)  
    return out


def on_request(ch, method, props, body):
    resp = json.loads(body)
    print(" [x] Received %r" % resp)
    output = fetcher(resp)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties( correlation_id=props.correlation_id), body=output)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Done")


if __name__ == '__main__':

    host = 'reindeer.rmq.cloudamqp.com'
    user = 'grbidwio'

    credentials = pika.PlainCredentials(user, 'ezWzEJkTWd-EFoH7SpKF49cWTbwbzl4S')
    parameters = pika.ConnectionParameters(host=host, virtual_host=user, credentials=credentials)
    channel = pika.BlockingConnection(parameters).channel()
    channel.queue_declare(queue='task_queue', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=on_request)

    print(' [*] Waiting for tasks. To exit press CTRL+C')
    channel.start_consuming()
