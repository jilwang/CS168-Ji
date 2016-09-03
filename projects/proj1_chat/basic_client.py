import socket
import sys

ip_addr = sys.argv[1]
port = sys.argv[2]

client_sock = socket.socket()
client_sock.connect((ip_addr, int(port)))

print "Say something:"
data = raw_input()
client_sock.send(data)
