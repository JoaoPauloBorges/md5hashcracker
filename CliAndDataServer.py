# HTTP Data Server
import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import urllib.parse as urlparse
from urllib.parse import parse_qs

import pika
import uuid
import json


HOST_NAME = '127.0.0.1' 
PORT_NUMBER = 3000 


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
        self.response = []
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


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if  '/list' in self.path:
            block = self.path.split('list/')[1]

            try:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open(f"temp{block}.txt", 'rb') as f: 
                    self.wfile.write(f.read())
            except Exception as e:
                print (e)

        if  '/search' in self.path:
            minion_rpc = MinionRPC()
            parsed = urlparse.urlparse(self.path)
            arg = parse_qs(parsed.query)['hash'][0]
            print(arg)
            msg = {'hash': arg, 'url': "http://127.0.0.1:3000/list/" }
            response = minion_rpc.call(msg)
            print(" [.] Got %r" % response)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response[0])
            return

            
def initFiles(f):
    import math
    print('initializing files...')
    lines = 0
    nFile = 0
    fileLength = 0
    for line in open(f, 'r', errors="ignore").readlines(  ): fileLength += 1
    print(fileLength)
    maxLines = math.ceil(fileLength/4)
    print('maxlines: ' + str(maxLines))

    with open(f, 'r', errors="ignore") as sf:
        temp = ''
        for line in sf:
            temp += line
            if lines == maxLines:
                with open(f"temp{nFile}.txt", 'w') as newFiles:
                    newFiles.write(temp)
                nFile+=1
                lines=0
                temp = ''
            lines+=1
        with open(f"temp{nFile}.txt", 'w') as newFiles:
            newFiles.write(temp)
    print('files initialized')

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-initF', type=bool, default=False)
    parser.add_argument('-file', type=str, default='rockyou.txt')
    args = parser.parse_args()

    if args.initF:
        initFiles(args.file)

    server = ThreadedHTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    try:
        print('Server is running')
        server.serve_forever()

    except KeyboardInterrupt:
        print ('[!] Server is terminated')
        server.server_close()
