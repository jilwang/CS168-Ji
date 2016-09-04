import utils
import socket
import select
import sys
import CustomSocket


class Client:
    def __init__(self, sock):
        self.sockets = {sys.stdin : CustomSocket.CustomSocket(sys.stdin),
                        sock : CustomSocket.CustomSocket(sock)}

    def parse_input(self, input_sock):
        custom_socket = self.sockets[input_sock]
        recv_buffer = custom_socket.recv_buffer
        recv_bytes = input_sock.recv_into(recv_buffer, utils.MESSAGE_LENGTH)

        if recv_bytes == 0:
            pass

        else:

            if input_sock is sys.stdin:
                data = utils.CLIENT_MESSAGE_PREFIX + \
                       recv_buffer[:(utils.MESSAGE_LENGTH -
                                     len(utils.CLIENT_MESSAGE_PREFIX))]

                # padding the message
                if len(data) < utils.MESSAGE_LENGTH:
                    data += ' ' * (utils.MESSAGE_LENGTH - len(data))

                return data

            else:
                if len(recv_buffer) < utils.MESSAGE_LENGTH:
                    return None

                data = recv_buffer[:utils.MESSAGE_LENGTH]
                recv_buffer = recv_buffer[utils.MESSAGE_LENGTH:]
                return data


    def send_data(self, data, output_sock):
        pass


def main():
    if len(sys.argv) < 5:
        raise "Insufficient number of client arguments. Need 5."

    name = sys.argv[2]
    addr = sys.argv[3]
    port = int(sys.argv[4])

    client_socket = socket.socket()
    client_socket.connect((addr, port))
    client = Client(client_socket)

    input_socks = [client_socket, sys.stdin]
    while True:
        input_ready, output_ready, error = \
            select.select(input_socks, [], [])

        for input_sock in input_ready:
            output_sock = None
            for (sock, custom) in client.sockets:
                if sock is not input_sock:
                    output_sock = sock
            assert output_sock

            data = client.parse_input(input_sock)

            # only send the data if it is valid
            if data:
                client.send_data(data, output_sock)

main()
