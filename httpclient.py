#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Modifications Copyright 2021 Robert MacGillivray
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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, headers="", body=""):
        self.code = code
        self.headers = headers
        self.body = body

    def __str__(self):
        return "--Code--\n{}\n--Headers--\n{}\n--Body--\n{}".format(self.code, self.headers, self.body)

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def get_code(self, data):
        return int(self.get_headers(data).split(" ")[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def end_sending(self):
        self.socket.shutdown(socket.SHUT_WR)
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # try to parse the given URL - return 400 if we can't (assume malformed URL)
        try:
            urlParts = urllib.parse.urlparse(url)
        except:
            print("Could not parse [{}]".format(url))
            return HTTPResponse(400)

        # if we didn't get a properly parseable request, return 400
        if not urlParts or not urlParts.hostname:
            print("Some key URL parts missing after parsing.")
            return HTTPResponse(400)

        # try to get the port number if present (assume port 80 otherwise)
        port = 80
        if urlParts.port:
            port = urlParts.port

        # try to connect to host - return 404 if we can't
        try:
            #print("Connecting to: [{}:{}]".format(urlParts.hostname, port))
            self.connect(urlParts.hostname, port)
        except:
            print("Could not connect to [{}:{}]".format(urlParts.hostname, port))
            self.close()
            return HTTPResponse(404)

        # handle the case where a URL doesn't have a trailing / (like http://slashdot.org)
        path = "/"
        if urlParts.path:
            path = urlParts.path

        # try to send request to host
        try:
            self.sendall("GET {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, urlParts.hostname))
            self.end_sending()
        except:
            print("Error sending bytes to host.")
            self.close()
            return None

        # try receiving response from host
        try:
            response = self.recvall()
        except:
            print("Error handling host response.")
            self.close()
            return None

        #print ("SUCCESS:\n{}".format(HTTPResponse(self.get_code(response), self.get_headers(response), self.get_body(response))))
        self.close()
        # Success! Return whatever we got from the host.
        return HTTPResponse(self.get_code(response), self.get_headers(response), self.get_body(response))

    def POST(self, url, args=None):
        # try to parse the given URL - return 400 if we can't (assume malformed URL)
        try:
            urlParts = urllib.parse.urlparse(url)
        except:
            print("Could not parse [{}]".format(url))
            return HTTPResponse(400)

        # if we didn't get a properly parseable request, return 400
        if not urlParts or not urlParts.hostname:
            print("Some key URL parts missing after parsing.")
            return HTTPResponse(400)

        # try to get the port number if present (assume port 80 otherwise)
        port = 80
        if urlParts.port:
            port = urlParts.port

        # try to connect to host - return 404 if we can't
        try:
            #print("Connecting to: [{}:{}]".format(urlParts.hostname, port))
            self.connect(urlParts.hostname, port)
        except:
            print("Could not connect to [{}:{}]".format(urlParts.hostname, port))
            self.close()
            return HTTPResponse(404)

        # handle the case where a URL doesn't have a trailing / (like http://slashdot.org)
        path = "/"
        if urlParts.path:
            path = urlParts.path

        # try to send request to host
        try:
            if args:
                urlEncodedData = urllib.parse.urlencode(args)
                #print("Args: [{}]\nEncoded: [{}]".format(args, urlEncodedData))
                self.sendall("POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}".format(path, urlParts.hostname, sys.getsizeof(urlEncodedData), urlEncodedData))
            else:
                self.sendall("POST {} HTTP/1.1\r\nHost: {}\r\nContent-Length: 0\r\n".format(path, urlParts.hostname))
            self.end_sending()
        except:
            print("Error sending bytes to host.")
            self.close()
            return None

        # try receiving response from host
        try:
            response = self.recvall()
        except:
            print("Error handling host response.")
            self.close()
            return None

        #print ("SUCCESS:\n{}".format(HTTPResponse(self.get_code(response), self.get_headers(response), self.get_body(response))))
        self.close()
        # Success! Return whatever we got from the host.
        return HTTPResponse(self.get_code(response), self.get_headers(response), self.get_body(response))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        elif (command == "GET"):
            return self.GET( url, args )
        else:
            return "This client cannot handle {} requests.".format(command)
    
if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
