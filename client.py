import socket

HOST = 'localhost'
PORT = 9999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True :
        temp = input()
        bitowo = temp.encode()
        s.send(bitowo)
        data = s.recv(1024)
        print('Received', repr(data))

