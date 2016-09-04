import utils
import socket
import select
import sys
import helper


class Client:
    def __init__(self, sock):
        self.sockets = {sys.stdin: helper.CustomSocket(sys.stdin),
                        sock: helper.CustomSocket(sock)}

    def parse_input(self, input_sock):
        custom_socket = self.sockets[input_sock]
        recv_buffer = custom_socket.recv_buffer

        if input_sock is sys.stdin:
            recv_bytes = raw_input()
            if len(recv_bytes) < utils.MESSAGE_LENGTH:
                recv_bytes += ' ' * (utils.MESSAGE_LENGTH - len(recv_bytes))
            recv_buffer += recv_bytes
            data = recv_buffer[:utils.MESSAGE_LENGTH]
            del recv_buffer[:utils.MESSAGE_LENGTH]
            return data

        else:
            recv_bytes = input_sock.recv(utils.MESSAGE_LENGTH)

            if len(recv_bytes) == 0:
                raise ValueError("Server disconnected.")

            recv_buffer += recv_bytes

            if len(recv_buffer) < utils.MESSAGE_LENGTH:
                return None

            data = recv_buffer[:utils.MESSAGE_LENGTH]
            del recv_buffer[:utils.MESSAGE_LENGTH]
            return data


def main():
    if len(sys.argv) < 4:
        raise BaseException("Insufficient number of client arguments. Need 5.")

    name = sys.argv[1]
    addr = sys.argv[2]
    port = int(sys.argv[3])

    client_socket = socket.socket()

    try:
        client_socket.connect((addr, port))
    except socket.error as err:
        error_msg = utils.CLIENT_CANNOT_CONNECT.format(addr, port)
        helper.print_stdout(error_msg)
        sys.exit()

    client = Client(client_socket)

    # new special message that creates the name for the client
    client_socket.send(name)  # make it a blocking call

    interfaces = [client_socket, sys.stdin]
    helper.print_stdout(utils.CLIENT_MESSAGE_PREFIX)
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
                helper.print_stdout(error_msg)
                sys.exit()

            if data:
                if input_sock is sys.stdin:
                    output_sock.sendall(data)
                else:
                    data = data.rstrip()
                    server_msg = utils.CLIENT_WIPE_ME + '\r' + data
                    helper.print_stdout(server_msg)
                    if data:
                        helper.print_stdout('\n')
                helper.print_stdout(utils.CLIENT_MESSAGE_PREFIX)

main()
