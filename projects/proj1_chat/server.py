import utils
import select
import socket
import sys
import string
import helper


class Server:
    def __init__(self, sock):
        self.channels = {}
        self.server_socket = helper.CustomSocket(sock)
        self.client_sockets = {}

    def read_input(self, input_socket):
        client_buffer = self.client_sockets[input_socket].recv_buffer
        recv_bytes = input_socket.recv(utils.MESSAGE_LENGTH)

        if len(recv_bytes) == 0:
            name = self.client_sockets[input_socket].name
            channel = self.client_sockets[input_socket].channel

            self.client_sockets.pop(input_socket, None)
            if channel in self.channels:
                self.channels[channel].remove(input_socket)
                leave_msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(name)
                self.broadcast(helper.pad_msg(leave_msg), channel, input_socket)

        client_buffer += recv_bytes

        if len(client_buffer) < utils.MESSAGE_LENGTH:
            return None
        else:
            data = client_buffer[:utils.MESSAGE_LENGTH]
            del client_buffer[:utils.MESSAGE_LENGTH]
            return data

    def dispatch(self, data, sock):

        if data[0] is not '/':
            self.chat(data, sock)

        else:
            self.control(data, sock)

    def chat(self, data, sock):
        channel = self.client_sockets[sock].channel
        name = '[' + self.client_sockets[sock].name + '] '
        data = name + data
        if channel:
            self.broadcast(data, channel, sock)
        else:
            error_msg = utils.SERVER_CLIENT_NOT_IN_CHANNEL
            sock.sendall(helper.pad_msg(error_msg))

    def control(self, data, sock):
        segments = data.split()

        if segments[0] == '/list':
            self.list_control(sock)

        elif segments[0] == '/join':
            if len(segments) >= 2:
                self.join_control(sock, segments[1])
            else:
                error_msg = utils.SERVER_JOIN_REQUIRES_ARGUMENT
                sock.sendall(helper.pad_msg(error_msg))

        elif segments[0] == '/create':
            if len(segments) >= 2:
                self.create_control(sock, segments[1])
            else:
                error_msg = utils.SERVER_CREATE_REQUIRES_ARGUMENT
                sock.sendall(helper.pad_msg(error_msg))

        else:
            error_msg = utils.SERVER_INVALID_CONTROL_MESSAGE \
                .format(data)
            sock.sendall(helper.pad_msg(error_msg))

    def broadcast(self, data, channel, sock):
        if not channel or channel not in self.channels:
            return

        output_sockets = self.channels[channel]
        for output_socket in output_sockets:
            if sock != output_socket:
                output_socket.sendall(helper.pad_msg(data))

    def list_control(self, sock):
        channel_list = [channel for channel in self.channels]
        list_msg = string.join(channel_list, '\n')
        sock.sendall(helper.pad_msg(list_msg))

    def join_control(self, sock, channel):
        if channel not in self.channels:
            error_msg = utils.SERVER_NO_CHANNEL_EXISTS.format(channel)
            sock.sendall(helper.pad_msg(error_msg))
            return

        client_socket = self.client_sockets[sock]
        name = client_socket.name
        old_channel = client_socket.channel

        if old_channel:
            self.channels[old_channel].remove(sock)
            leave_msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(name)
            self.broadcast(helper.pad_msg(leave_msg), old_channel, sock)

        join_msg = utils.SERVER_CLIENT_JOINED_CHANNEL.format(name)
        self.broadcast(helper.pad_msg(join_msg), channel, sock)
        self.channels[channel].append(sock)
        client_socket.channel = channel

    def create_control(self, sock, channel):
        if channel in self.channels:
            error_msg = utils.SERVER_CHANNEL_EXISTS.format(channel)
            sock.sendall(helper.pad_msg(error_msg))
            return

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
                new_client_custom_socket = helper.\
                    CustomSocketAdv(new_client_socket)

                # blocking call for the name of the client
                while True:
                    recv_bytes = new_client_socket.recv(utils.MESSAGE_LENGTH)
                    new_client_custom_socket.recv_buffer += recv_bytes

                    if len(new_client_custom_socket.recv_buffer) \
                            >= utils.MESSAGE_LENGTH:
                        new_client_custom_socket.name = \
                            new_client_custom_socket.recv_buffer[:utils.MESSAGE_LENGTH].rstrip()
                        del new_client_custom_socket.recv_buffer[:utils.MESSAGE_LENGTH]
                        server.client_sockets[new_client_socket] = \
                            new_client_custom_socket
                        break

            else:
                try:
                    data = server.read_input(sock)

                except ValueError as err:
                    name = server.client_sockets[sock].name
                    channel = server.client_sockets[sock].channel
                    server.client_sockets.pop(sock, None)
                    left_msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(name)
                    server.broadcast(helper.pad_msg(left_msg), channel, sock)
                    continue

                if data:
                    data = str(data).rstrip()
                    server.dispatch(data, sock)


main()
