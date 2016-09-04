import utils
import socket
import select
import sys
import CustomSocket


class Client:
    def __init__(self, sock):
        self.sockets = {sys.stdin: CustomSocket.CustomSocket(sys.stdin),
                        sock: CustomSocket.CustomSocket(sock)}

    def parse_input(self, input_sock):
        custom_socket = self.sockets[input_sock]
        recv_buffer = custom_socket.recv_buffer

        if input_sock is sys.stdin:
            recv_bytes = raw_input()
            recv_buffer += recv_bytes
            data = recv_buffer[:(utils.MESSAGE_LENGTH -
                                 len(utils.CLIENT_MESSAGE_PREFIX))]

            return data

        else:
            recv_bytes = input_sock.recv(utils.MESSAGE_LENGTH)
            recv_buffer += recv_bytes

            if len(recv_buffer) < utils.MESSAGE_LENGTH:
                return None

            data = recv_buffer[:utils.MESSAGE_LENGTH]
            recv_buffer = recv_buffer[utils.MESSAGE_LENGTH:]
            return data


def main():
    if len(sys.argv) < 4:
        raise BaseException("Insufficient number of client arguments. Need 5.")

    name = sys.argv[1]
    addr = sys.argv[2]
    port = int(sys.argv[3])

    client_socket = socket.socket()
    client_socket.connect((addr, port))
    client = Client(client_socket)

    # new special message that creates the name for the client
    client_socket.send(name)  # make it a blocking call

    interfaces = [client_socket, sys.stdin]
    while True:

        # read data into buffer from available sockets
        input_ready, output_ready, error = \
            select.select(interfaces, [], [])

        for input_sock in input_ready:
            output_sock = None
            for sock in client.sockets:
                if sock is not input_sock:
                    output_sock = sock
            assert output_sock

            try:
                data = client.parse_input(input_sock)
            except ValueError as err:
                assert input_sock is not sys.stdin
                error_msg = utils.CLIENT_SERVER_DISCONNECTED.format(addr, port)
                sys.stdout.write(error_msg)
                sys.exit()

            if data:
                if input_sock is sys.stdin:
                    data = CustomSocket.pad_msg(data)
                    output_sock.sendall(data)
                else:
                    sys.stdout.write(data.rstrip())

main()
