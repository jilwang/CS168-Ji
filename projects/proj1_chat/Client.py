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
            return None

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

    def send_data(self, output_sock):
        send_buffer = self.sockets[output_sock].send_buffer
        if len(send_buffer) < utils.MESSAGE_LENGTH:
            return None

        data = str(send_buffer[:utils.MESSAGE_LENGTH])
        send_buffer = send_buffer[utils.MESSAGE_LENGTH:]

        if output_sock is sys.stdin:
            output_sock.send(data)
        else:
            sys.stdout.send(data.rstrip())

    def buffer_output_data(self, data, output_sock):
        send_buffer = self.sockets[output_sock].send_buffer
        send_buffer += data


def main():
    if len(sys.argv) < 5:
        raise "Insufficient number of client arguments. Need 5."

    name = sys.argv[2]
    addr = sys.argv[3]
    port = int(sys.argv[4])

    client_socket = socket.socket()
    client_socket.connect((addr, port))
    client = Client(client_socket)

    # new special message that creates the name for the client
    name_msg = "/name " + name
    if len(name_msg) < utils.MESSAGE_LENGTH:
        name_msg += ' ' * (utils.MESSAGE_LENGTH - len(name_msg))
    client_socket.send(name_msg)  # make it a blocking call

    interfaces = [client_socket, sys.stdin]
    while True:

        # read data into buffer from available sockets
        input_ready, output_ready, error = \
            select.select(interfaces, [], [])

        for input_sock in input_ready:
            output_sock = None
            for (sock, custom) in client.sockets:
                if sock is not input_sock:
                    output_sock = sock
            assert output_sock

            data = client.parse_input(input_sock)
            if not data:
                assert output_sock is sys.stdin
                error_msg = utils.CLIENT_SERVER_DISCONNECTED.format(addr, port)
                sys.stdout.write(error_msg)
                sys.exit()

            client.buffer_output_data(data, output_sock)

        # send buffered data to available sockets
        input_ready, output_ready, error = \
            select.select([], interfaces, [])
        
        for output_sock in output_ready:
            client.send_data(output_sock)


main()
