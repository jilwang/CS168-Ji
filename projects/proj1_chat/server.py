import utils
import select
import socket
import sys
import CustomSocket


class Server:
    def __init__(self, sock):
        self.channels = {}
        self.server_socket = CustomSocket.CustomSocket(sock)
        self.client_socket = []

    def parse(self, data, client_socket):
        pass


if len(sys.argv) < 2:
    raise "Insufficient server arguments."

server_socket = socket.socket()
port = sys.argv[1] 
server_socket.bind(('localhost', int(port)))
server_socket.listen(5)

server = Server(server_socket)

while True:
    listen_set = server.client_socket[:]
    listen_set.append(server.server_socket)

    readable, writable, error = \
        select.select(listen_set, [], [])

    if server.server_socket in readable:

    for sock in readable:
        if sock.socket is server.server_socket:
            (new_client, addr) = server.server_socket.accept()
            server.client_socket.append(CustomSocket.CustomSocketAdv(new_client))

        else:
            client_socket = sock.socket
            recv_bytes = client_socket.recv_into(sock.recv_buffer, utils.MESSAGE_LENGTH)
            if recv_bytes == 0:
                pass
            elif len(sock.recv_buffer) < utils.MESSAGE_LENGTH:
                pass
            else:
                data = sock.recv_buffer[:utils.MESSAGE_LENGTH]
                recv_buffer = sock.recv_buffer[200:]
                server.parse(data, sock)
            
