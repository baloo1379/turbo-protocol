import socket
import random
import sys
from protocol import Turbo, OPERATORS


DEBUG = False

HOST, PORT = "localhost", 9999

MIN = -2147483648
MAX = 2147483647


def debugger(*msgs):
    if DEBUG:
        result = "DEBUG:"
        for el in msgs:
            result += " "+str(el)
        print(result)


def client(host, port):
    host = host
    port = port
    addr = (host, port)
    tur = Turbo()
    turbo_received = Turbo()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(addr)
        except OSError as refused:
            print(f'Something went wrong: {refused.strerror}, code: [{refused.errno}], address: {addr}')
        else:
            print("Connected to", socket.gethostbyaddr(host)[0])
            res = "Available operations"
            for op in OPERATORS:
                res += ", "+op
            print(res)
            print("Please always write sign after first number and all separated space: ")
            rand = random.randrange(1, 1024)
            while True:

                # Wysyłanie
                eq = input()
                if eq == "EXIT" or eq == "Exit" or eq == "exit":
                    s.shutdown(socket.SHUT_RDWR)
                    print("exiting successful")
                    break

                eq = eq.split(" ")
                try:
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
                        if sign == OPERATORS[7] or sign == OPERATORS[8]:
                            first = int(eq[0])
                            second = 0
                            if type(eq[0]) == int and (eq[1] == "!" or  eq[1] == "NOT"):
                                if int(eq[0]) > MAX or int(eq[0]) < MIN:
                                    print("number is too big! expected number between -2147483648 and 2147483647 ")
                                    continue
                        else:
                            print("Too few arguments, expected 3 arguments.")
                            continue
                    elif len(eq) < 2:
                        print("Too few arguments, should be at least 2")
                        continue
                except ValueError:
                    print("That is not valid number.")
                    continue

                temp_items = [sign, first, second]
                debugger(temp_items)

                debugger("rand: " + str(rand))

                try:
                    tur = Turbo(temp_items[0], 1, rand, True, temp_items[1], temp_items[2])
                except ValueError as sign_error:
                    print(f'Something went wrong: {sign_error}')
                    continue

                debugger("Packet: " + tur.print())
                s.sendall(tur.pack_packet())

                # Odbieranie
                data_received = s.recv(128)
                turbo_received.parse_data(data_received)

                if turbo_received.session_id == rand:
                    if turbo_received.status == 2:
                        if sign == "!":
                            print(turbo_received.second)
                        elif sign == "abs":
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
                    elif turbo_received.status == 6:
                        debugger("error, factorial result too big, but still have NOT result")
                        if sign == "!":
                            print("error, can't calculate factorial from given argument")
                        elif sign == "abs":
                            print(turbo_received.first)
                        else:
                            print(turbo_received.first)
                    elif turbo_received.status == 7:
                        print("error, division by 0")
                else:
                    print("different session id than sent")

            # while end
            debugger("wyszełem z while")


if __name__ == "__main__":
    args = sys.argv
    host = args[1] if len(args) > 1 else HOST
    port = int(args[2]) if len(args) > 2 else PORT

    client(host, port)
    input("Press ENTER to continue...")
    sys.exit()
