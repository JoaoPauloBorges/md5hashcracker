# HTTP Data Server
import http.server
import os, cgi

HOST_NAME = '127.0.0.1' 
PORT_NUMBER = 3000 


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.path)
        if  '/list' in self.path:
            block = self.path.split('list/')[1]
            print(block)
            try:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open(f"temp{block}.txt", 'rb') as f: 
                    self.wfile.write(f.read())
            except Exception as e:
                print (e)
            
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

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-initF', type=bool, default=False)
    parser.add_argument('-file', type=str, default='rockyou.txt')
    args = parser.parse_args()

    if args.initF:
        initFiles(args.file)

    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    try:
        print('Server is running')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ('[!] Server is terminated')
        httpd.server_close()
