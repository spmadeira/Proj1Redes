import socket
from threading import Thread
import os.path

HOST = '0.0.0.0'
PORT = 6789

SERVE = dict({
    'html': 'text/html',
    'ico': 'image/x-icon',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'js': 'text/javascript',
    'css': 'text/css'
})

class HttpMessage(object):
    def __init__(self, method, route, headers, body):
        self.method = method
        self.route = route
        self.headers = headers
        self.body = body


def parse(http):
    parts = http.split('\r\n\r\n')

    if len(parts) > 1:
        heading = parts[0]
        body = parts[1]
    else:
        heading = parts[0]
        body = '' 

    info = heading.split('\r\n')
    method, route, version = info.pop(0).split(' ')
    headers = { }
    for header in info:
        key, value = header.split(': ')
        headers[key] = value

    return HttpMessage(method, route, headers, body)

    
def respond(msg):
    if not msg.method == 'GET':
        return 'HTTP/1.0 405 Method Not Allowed\ncontent-type: application/problem'.encode()

    route = msg.route[1:]

    if not route:
        route = 'Index.html'

    if len(route.split('.')) == 1: # If has no defined file format
        file_name = './View/{0}.html'.format(route)
    else: 
        file_name = './View/{0}'.format(route)

    requested_format = file_name.split('.')[-1]

    if requested_format not in dict.keys(SERVE):
        'HTTP/1.0 500 Internal Server Error\ncontent-type: application/problem'.encode()

    if os.path.isfile(file_name):
        try:
            f = open(file_name, "rb")
            content = f.read()
            return 'HTTP/1.0 200 OK\ncontent-type: {0}\n\n'.format(SERVE[requested_format]).encode()+content
        except IOError:
            return 'HTTP/1.0 500 Internal Server Error\ncontent-type: application/problem'.encode()
        else:
            f.close()
    else:
        return 'HTTP/1.0 404 Not Found\ncontent-type: application/problem\n\nFile Not Found'.encode()


def handle_request(req, conn):
    msg = parse(req)
    print(msg.route)
    res = respond(msg)
    conn.sendall(res)
    conn.close()


#####

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
