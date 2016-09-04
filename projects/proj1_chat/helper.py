import socket
import utils
import sys


class CustomSocket:
    def __init__(self, sock):
        self.socket = sock
        self.recv_buffer = bytearray()


class CustomSocketAdv(CustomSocket):
    def __init__(self, sock):
        CustomSocket.__init__(self, sock)
        self.channel = ""
        self.name = ""


def pad_msg(msg):
    if len(msg) < utils.MESSAGE_LENGTH:
        msg += ' ' * (utils.MESSAGE_LENGTH - len(msg))
    return msg


def print_stdout(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
