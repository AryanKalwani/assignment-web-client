#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it


# Resources used:
# https://www.internalpointers.com/post/making-http-requests-sockets-python
# https://www.urlencoder.io/python/
# https://stackoverflow.com/questions/45695168/send-raw-post-request-using-socket


import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        arr = data.split()
        code = int(arr[1])
        return code

    def get_headers(self,data):
        arr = data.split("\r\n\r\n")
        return arr[0]

    def get_body(self, data):
        arr = data.split("\r\n\r\n")
        return arr[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        self.connect(parsed_url.hostname, 80 if parsed_url.port==None else parsed_url.port)
        upath = '/' if parsed_url.path=='' else parsed_url.path
        query_params = "?"
        if args:
            for k,v in args.items():
                query_params += '{}={}&'.format(k,v)
            query_params = query_params[:-1]
            upath += query_params
        req = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(upath, parsed_url.hostname)
        print("Request is ", req)
        self.sendall(req)
        res = self.recvall(self.socket)
        print("Response is ", res)
        code = self.get_code(res)
        print("Response code is ", code)
        headers = self.get_headers(res)
        print("Response headers are ", headers)
        body = self.get_body(res)
        print("Response body is ", body)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        self.connect(parsed_url.hostname, 80 if parsed_url.port==None else parsed_url.port)
        if args:
            args = urllib.parse.urlencode(args)
        req = 'POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n{}'.format(
            '/' if parsed_url.path=='' else parsed_url.path, parsed_url.hostname, 0 if args==None else len(args), args)
        self.sendall(req)
        res = self.recvall(self.socket)
        print("Response is ", res)
        code = self.get_code(res)
        print("Response code is ", code)
        headers = self.get_headers(res)
        print("Response headers are ", headers)
        body = self.get_body(res)
        print("Response body is ", body)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
