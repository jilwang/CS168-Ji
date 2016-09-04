import utils
import select
import socket
import sys
import CustomSocket


class Server:
    def __init__(self, sock):
        self.channels = {}
        self.server_socket = CustomSocket.CustomSocket(sock)
        self.client_sockets = {}

    def read_input(self, data, input_socket):
        pass

    def send_output(self, output_socket):
        pass

    def buffer_output_data(self, data, output_socket):
        pass


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
                print len(server.client_sockets)
                print client_name
                print "Done"

            else:
                pass
                # client_socket = server.client_sockets[sock]
                # recv_bytes = sock.recv_into(client_socket.recv_buffer,
                #                             utils.MESSAGE_LENGTH)
                # if recv_bytes == 0:
                #     pass
                # elif len(client_socket.recv_buffer) < utils.MESSAGE_LENGTH:
                #     pass
                # else:
                #     data = sock.recv_buffer[:utils.MESSAGE_LENGTH]
                #     recv_buffer = client_socket.recv_buffer[200:]
                #     server.parse(data, sock)

main()
