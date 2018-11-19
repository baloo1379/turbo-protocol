import socket
import random
from protocol import Turbo


DEBUG = True
MIN = -2147483648
MAX = 2147483647

def debugger(msg):
    if DEBUG:
        print("DEBUG:", msg)


if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 9999
    tur = Turbo()
    turbo_received = Turbo()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Please always write sign after first number and all separated space: ")
        rand = random.randrange(1, 1024)
        while True:

            #Wysyłanie
            eq = input()
            if eq == "EXIT" or eq == "Exit" or eq == "exit":
                s.shutdown(socket.SHUT_RDWR)
                print("exiting succesful")
                break

            eq = eq.split(" ")
            if len(eq) > 3:
                print("Too many arguments. Expected 3 arguments. ")
                continue
            elif len(eq) == 3:
                first = int(eq[0])
                second = int(eq[2])
                sign = eq[1]
                if first > MAX or first < MIN or second > MAX or second < MIN:
                    print("number is too big! expected number between -2147483648 and 2147483647 ")
                    continue

            elif len(eq) == 2:
                sign = eq[1]
                first = int(eq[0])
                second = 0
                if type(eq[0]) == int and (eq[1] == "!" or  eq[1] == "NOT"):
                    if int(eq[0]) > MAX or int(eq[0]) < MIN:
                        print("number is too big! expected number between -2147483648 and 2147483647 ")
                        continue


            temp_items = [sign, first, second]
            debugger(temp_items)

            debugger("rand: " + str(rand))

            tur = Turbo(temp_items[0], 1, rand, True, temp_items[1], temp_items[2])
            tur.pack_packet()
            debugger("Packet: " + tur.print())
            s.sendall(tur.pack_packet())
            #Odbieranie
            data_received = s.recv(8192)
            turbo_received.parse_data(data_received)

#sprawdzisc status czy jest to 2 nagranie 50s
            if turbo_received.session_id == rand:
                if turbo_received.status == 2:
                    if sign == "!":
                        print(turbo_received.second)
                    elif sign == "NOT":
                        print(turbo_received.first)
                    else:
                        print(turbo_received.first)
                elif turbo_received.status == 3:
                    print("general error")
                    continue
                elif turbo_received.status == 4:
                    print("error, result is too big")
                elif turbo_received.status == 5:
                    print("error, wrong status")
            else:
                print("different session id than sent")




        debugger("wyszełem z while")
