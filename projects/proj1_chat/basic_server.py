import socket

server_socket = socket.socket()
server_socket.bind(('localhost', 12345))
server_socket.listen(5)

while True:
    (new_sock, addr) = server_socket.accept()
    data = new_sock.recv(1024)

    print data
