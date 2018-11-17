import socket
import random

from protocol import Turbo

DEBUG = True


def debugger(msg):
    if DEBUG:
        print("DEBUG:", msg)


if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 9999
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:

            #Wysyłanie
            print("Please write 1st number: ")
            first = input()
            first = int(first)
            if first > 2147483647 or first < -2147483648:
                print("number is too big! expected number between -2147483648 and 2147483647 ")
                print("\ngive another number: ")
                first = input()
                first = int(first)
            print("\nPlease write second number: ")
            second = input()
            second = int(second)
            if second > 2147483647 or second < -2147483648:
                print("number is too big! expected number between -2147483648 and 2147483647 ")
                print("\ngive another number: ")
                second = input()
                second = int(second)
            print("\nPlease write sign of the activity: ")
            sign = input()

            temp_items = [sign, first, second]

            rand = random.randrange(1,1024)

            tur = Turbo(temp_items[0], 1, rand, True, temp_items[1], temp_items[2])
            s.send(tur.pack_packet())
            #Odbieranie
            data_received = s.recv(1024)
            turbo_received = Turbo()
            turbo_received = turbo_received.parse_data(data_received)

            if turbo_received.session_id == rand:
                print(turbo_received.first)

            else:
                print("different session id than sent")
            if data_received == "EXIT" or data_received == "Exit" or data_received == "exit":
                s.shutdown(socket.SHUT_RDWR)
                print("exiting succesful")
                break
            else:
                print('Received', repr(data_received))
        debugger("wyszełem z while")
