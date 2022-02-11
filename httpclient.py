#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust and Anisha Sethumadhavan
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
#
# References:
# bgporter( 9 April 2011) and mb21(edited, 15 November 2018), CC BY-SA 4.0, https://stackoverflow.com/a/5607708
# alvas, 3 January 2014, CC BY-SA 3.0, https://stackoverflow.com/a/20901803
# Bigyan Karki, CMPUT 404 LAB 2, 17 January 2022, https://drive.google.com/file/d/1TD8UR9o-GPaudPNsY9HrePzroRBsEBFe/view
#
# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

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
        status_code = data.split()[1]
        #print("get_code data split  ", data.split())
        #print("get_code sc   ", status_code)
        return int(status_code)

    def get_headers(self, data):
        # headers end with "\r\n\r\n", so we split them
        #print("get_h split  ", data.split("\r\n\r\n"))
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        # body is below headers so we need to take data after "\r\n\r\n"
        body = data.split("\r\n\r\n")[1]
        return body
    
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

    """
    URlparser is a function that parses through the url
    :param url to be parsed
    :return port, path and host from the parsed url
    """
    def url_parser(self, url):
        # parse the url
        parsed_url = urllib.parse.urlparse(url)

        # get the port
        port = parsed_url.port
        if not parsed_url.port:
            port = 80

        # get the path
        path = parsed_url.path
        if parsed_url.path == "":
            path = "/"

        # get the host
        host = parsed_url.hostname
        return port, path, host

    def GET(self, url, args=None):
        #code = 500
        #body = ""
        port, path, host = self.url_parser(url)
        get_request_header = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: Closed\r\n\r\n'
        self.connect(host, port)
        self.sendall(get_request_header)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #code = 500
        #body = ""
        port, path, host = self.url_parser(url)
        #print("PoSt XXXXXXXXXXXXXXXXXXXX  ", port, path, host)
        self.connect(host, port)
        #print("connected")

        if args == None:
            content_length = str(0)
            payload = ""
        else:
            payload = (urllib.parse.urlencode(args))
            #print("payload  ", payload)
            content_length = str(len(payload))

        post_request_header = f'POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: Closed\r\nContent-Length: {content_length}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{payload}\r\n'

        self.sendall(post_request_header)
        #print("sendall")
        data = self.recvall(self.socket)
        #print("data   ", data)
        code = self.get_code(data)
        #print("code   ", code)
        body = self.get_body(data)
        self.close()
        print(body)
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
