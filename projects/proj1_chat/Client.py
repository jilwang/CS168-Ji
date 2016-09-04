import utils
import socket
import select
import sys


class Client:
    def __init__(self, sock):
        self.socket = sock
        self.recv_buffer_server = bytearray()
        self.recv_buffer_stdin = bytearray()
        self.send_buffer = bytearray()

if len(sys.argv) < 5:
    raise "Insufficient number of client arguments. Need 5."

name = sys.argv[2]
addr = sys.argv[3]
port = int(sys.argv[4])

client_socket = socket.socket()
client_socket.connect((addr, port))
client = Client(client_socket)

input_sock = [client_socket, sys.stdin]
while True:
    input_ready, output_ready, error = \
        select.select(input_sock, [], [])

    for sock in input_ready:
        if sock is sys.stdin:
