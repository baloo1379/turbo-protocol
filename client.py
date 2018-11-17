import socket

HOST = 'localhost'
PORT = 9999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        temp = input()
        bitowo = temp.encode()
        s.send(bitowo)
        data = s.recv(1024)
        translacja = data.decode()
        if (translacja == "EXIT" or translacja == "Exit" or translacja == "exit"):
            s.shutdown(socket.SHUT_RDWR)
            print("exiting succesful")
            break
        else:
            print('Received', repr(data))
    print("wyszełem z while")
