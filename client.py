import socket
import random
import sys
from protocol import Turbo, OPERATORS, MAX_INT, MIN_INT


DEBUG = False

HOST, PORT = "localhost", 9999

MIN = MIN_INT
MAX = MAX_INT


def debugger(*msgs):
    if DEBUG:
        result = "DEBUG:"
        for el in msgs:
            result += " "+str(el)
        print(result)


def client(host_ip, host_port):
    response = Turbo()
    sign = "+"
    first = 0
    second = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host_ip, host_port))
        except OSError as refused:
            print(f'Something went wrong: {refused.strerror}, code: [{refused.errno}], address: {(host_ip, host_port)}')
        else:
            print("Connected to", socket.gethostbyaddr(host_ip)[0])
            print("Please always write sign after first number and all separated space(only integers): ")
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
                            if type(eq[0]) == int and (eq[1] == "!" or eq[1] == "NOT"):
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

                temp_items = (sign, first, second)
                debugger(temp_items)

                debugger("rand:", str(rand))

                try:
                    query = Turbo(temp_items[0], 1, rand, temp_items[1], temp_items[2])
                except ValueError as err:
                    print(f'Something went wrong: {err}')
                    continue

                debugger("Query to server: " + query.print())
                try:
                    s.sendall(query.bytes)
                except OSError as os_err:
                    print(f'Something went wrong: {os_err}')
                    break

                # Odbieranie

                try:
                    data_received = s.recv(512)
                    response.parse(data_received)
                except ValueError as err:
                    debugger("parsing error")
                    print(f'Something went wrong: {err}')
                    continue
                debugger("response:", response.print())

                if response.session_id != rand:
                    print("different session id than sent")
                else:
                    if response.status == 2:
                        if sign == OPERATORS[8]:
                            # factorial
                            print(first, OPERATORS[8], "=", response.second)
                        elif sign == OPERATORS[7]:
                            print("|", first, "|", "=", response.first)
                        else:
                            print(first, sign, second, "=", response.first)
                    elif response.status == 3:
                        print("general error")
                        continue
                    elif response.status == 4:
                        print("error, result is too big")
                    elif response.status == 5:
                        print("error, wrong status")
                    elif response.status == 6:
                        debugger("error, factorial result too big, but still have ABS result")
                        if sign == "!":
                            print("error, can't calculate factorial from given argument")
                        elif sign == OPERATORS[7]:
                            print("|", first, "|", "=", response.first)
                        else:
                            print(first, sign, second, "=", response.first)
                    elif response.status == 7:
                        print("error, division by 0")
                    elif response.status == 8:
                        print("error, bad base or argument ")
                    else:
                        print("client error")
                        break
            # while end
            debugger("quiting...")


if __name__ == "__main__":
    args = sys.argv
    host = args[1] if len(args) > 1 else HOST
    port = int(args[2]) if len(args) > 2 else PORT

    client(host, port)
    input("Press ENTER to continue...")
    sys.exit()
