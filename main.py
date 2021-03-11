import socket
from threading import Thread
import os.path

class HttpMessage(object):
    def __init__(self, method, route, headers, body):
        self.method = method
        self.route = route
        self.headers = headers
        self.body = body


def parse(http):
    heading, body = http.split('\r\n\r\n')
    info = heading.split('\r\n')
    method, route, version = info.pop(0).split(' ')
    headers = { }
    for header in info:
        key, value = header.split(': ')
        headers[key] = value

    return HttpMessage(method, route, headers, body)


def respond(msg):
    if not msg.method == 'GET':
        print('{0} != GET'.format(msg.method))
        return 'HTTP/1.0 405 Method Not Allowed\ncontent-type: application/problem'
    route = msg.route[1:]

    if not route:
        route = 'Index'

    file_name = './View/{0}.html'.format(route)

    if os.path.isfile(file_name):
        try:
            f = open('./View/{0}.html'.format(route))
            content = f.read()
            return 'HTTP/1.0 200 OK\ncontent-type: text/html\n\n{0}'.format(content)
        except IOError:
            return 'HTTP/1.0 500 Internal Server Error\ncontent-type: application/problem'
        finally:
            f.close()
    else:
        return 'HTTP/1.0 404 Not Found\ncontent-type: application/problem\n\nFile Not Found'


def handle_request(req, conn):
    res = respond(parse(req)).encode()
    conn.sendall(res)
    conn.close()

HOST = '0.0.0.0'
PORT = 54321

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print('Listening on port %s ...' % PORT)

while True:
    conn, add = server_socket.accept()

    req = conn.recv(1024).decode()
    req_t = Thread(target=handle_request, args=(req,conn))
    req_t.start()
