import utils
import select
import socket
import sys
import string
import CustomSocket


class Server:
    def __init__(self, sock):
        self.channels = {}
        self.server_socket = CustomSocket.CustomSocket(sock)
        self.client_sockets = {}

    def read_input(self, input_socket):
        client_buffer = self.client_sockets[input_socket].recv_buffer
        recv_bytes = input_socket.recv(utils.MESSAGE_LENGTH)
        client_buffer += recv_bytes

        if len(client_buffer) < utils.MESSAGE_LENGTH:
            return None
        else:
            data = client_buffer[:utils.MESSAGE_LENGTH]
            client_buffer = client_buffer[utils.MESSAGE_LENGTH:]
            return data

    def dispatch(self, data, sock):

        if data[0] is not '/':
            self.chat(data, sock)

        else:
            self.control(data, sock)

    def chat(self, data, sock):
        channel = self.client_sockets[sock].channel
        if channel:
            self.broadcast(data, channel)
        else:
            error_msg = utils.SERVER_CLIENT_NOT_IN_CHANNEL
            sock.sendall(CustomSocket.pad_msg(error_msg))

    def control(self, data, sock):
        segments = data.split()

        if segments[0] == '/list':
            self.list_control(sock)

        elif segments[0] == '/join':
            if len(segments) >= 2:
                self.join_control(sock, segments[1])
            else:
                error_msg = utils.SERVER_JOIN_REQUIRES_ARGUMENT
                sock.sendall(CustomSocket.pad_msg(error_msg))

        elif segments[0] == '/create':
            if len(segments) >= 2:
                self.create_control(sock, segments[1])
            else:
                error_msg = utils.SERVER_CREATE_REQUIRES_ARGUMENT
                sock.sendall(CustomSocket.pad_msg(error_msg))

        else:
            error_msg = utils.SERVER_INVALID_CONTROL_MESSAGE \
                .format(data)
            sock.sendall(CustomSocket.pad_msg(error_msg))

    def broadcast(self, data, channel):
        assert channel in self.channels
        output_sockets = self.channels[channel]
        for output_socket in output_sockets:
            output_socket.sendall(data)

    def list_control(self, sock):
        channel_list = [channel for channel in self.channels]
        list_msg = string.join(channel_list, '\n')
        sock.sendall(CustomSocket.pad_msg(list_msg))

    def join_control(self, sock, channel):
        if channel not in self.channels:
            error_msg = utils.SERVER_NO_CHANNEL_EXISTS.format(channel)
            sock.sendall(CustomSocket.pad_msg(error_msg))

        client_socket = self.client_sockets[sock]
        name = client_socket.name
        old_channel = client_socket.channel

        if old_channel:
            self.channels[old_channel].remove(sock)
            leave_msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(name)
            self.broadcast(CustomSocket.pad_msg(leave_msg), old_channel)

        self.channels[channel].append(sock)
        join_msg = utils.SERVER_CLIENT_JOINED_CHANNEL.format(name)
        self.broadcast(CustomSocket.pad_msg(join_msg), channel)

    def create_control(self, sock, channel):
        if channel in self.channels:
            error_msg = utils.SERVER_CHANNEL_EXISTS.format(channel)
            sock.sendall(CustomSocket.pad_msg(error_msg))

        self.channels[channel] = []
        self.join_control(sock, channel)


def main():
    if len(sys.argv) < 2:
        raise BaseException("Insufficient server arguments.")

    server_socket = socket.socket()
    port = sys.argv[1]
    server_socket.bind(('localhost', int(port)))
    server_socket.listen(5)

    server = Server(server_socket)

    while True:
        listen_set = [sock for sock in server.client_sockets]
        listen_set.append(server_socket)

        readable, writable, error = \
            select.select(listen_set, [], [])

        for sock in readable:
            if sock is server_socket:
                (new_client_socket, addr) = sock.accept()
                new_client_custom_socket = CustomSocket.\
                    CustomSocketAdv(new_client_socket)

                # blocking call for the name of the client
                client_name = new_client_socket.recv(utils.MESSAGE_LENGTH)
                new_client_custom_socket.name = client_name
                server.client_sockets[new_client_socket] = \
                    new_client_custom_socket

            else:
                try:
                    data = str(server.read_input(sock))

                except ValueError as err:
                    name = server.client_sockets[sock].name
                    channel = server.client_sockets[sock].channel
                    server.client_sockets.pop(sock, None)
                    left_msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(name)
                    server.broadcast(CustomSocket.pad_msg(left_msg), channel)
                    continue

                data = data.rstrip()
                server.dispatch(data, sock)


main()
