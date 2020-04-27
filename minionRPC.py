#!/usr/bin/env python
import pika
import uuid
import json

class MinionRPC(object):

    def __init__(self):
        user = 'grbidwio'
        credentials = pika.PlainCredentials(user, 'ezWzEJkTWd-EFoH7SpKF49cWTbwbzl4S')
        parameters = pika.ConnectionParameters(host='reindeer.rmq.cloudamqp.com', virtual_host=user, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)

        self.numBlocks = 4
        self.response = []
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response.append(body)

    def call(self, msg):
        self.response.clear()
        self.corr_id = str(uuid.uuid4())
        self.doSend(msg)

        while not self.checkResponse():
            self.connection.process_data_events()
        return self.response

    def doSend(self, msg):
        for i in range(self.numBlocks):
            self.channel.basic_publish(
                exchange='',
                routing_key='task_queue',
                body=json.dumps(self.generateUri(msg, i)),
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                    delivery_mode=2,  # make message persistent
                ))
    
    def generateUri(self, msg, i):
        newMsg = msg.copy()
        newMsg['url'] += str(i)
        return newMsg

    def checkResponse(self):
        if self.response == None:
            return False
        for resp in self.response:
           if "password found" in resp.decode("utf-8"):
                self.channel.queue_purge('task_queue')
                return True
        return self.response.__len__() == self.numBlocks

minion_rpc = MinionRPC()
while True:
    print("search a password")
    inpt = input()
    print(f"Requesting for {inpt}")
    msg = {'hash': inpt, 'url': "http://127.0.0.1:3000/list/" }
    response = minion_rpc.call(msg)
    print(" [.] Got %r" % response)