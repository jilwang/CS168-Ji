import socket


class CustomSocket:
    def __init__(self, sock):
        self.socket = sock
        self.recv_buffer = bytearray()
        self.send_buffer = bytearray()


class CustomSocketAdv(CustomSocket):
    def __init__(self, sock):
        CustomSocket.__init__(self, sock)
        self.channel = ""
        self.name = ""
