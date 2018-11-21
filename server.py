import socketserver
import socket
import copy
import sys
from math import factorial, pow, log, fabs
from protocol import Turbo, OPERATORS


DEBUG = False

HOST, PORT = "localhost", 9999

MAX_INT = 2147483647
MIN_INT = -2147483648

GENERAL_ERROR = Turbo("+", 3, 0, False, 0, 0)
SIZE_ERROR = Turbo("+", 4, 0, False, 0, 0)
STATUS_ERROR = Turbo("+", 5, 0, False, 0, 0)


def debugger(*msgs):
    if DEBUG:
        result = "DEBUG:"
        for el in msgs:
            result += " "+str(el)
        print(result)


class TurboProtocolTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        debugger("Handle entered")
        print("Connected with", socket.gethostbyaddr(self.client_address[0])[0], "from", self.client_address[0],
              "on port", self.client_address[1])
        query = Turbo()
        session_id = -1

        while True:
            debugger("Waiting for client")
            errors = 0

            # receiving data
            try:
                data_received = self.request.recv(8192)
                debugger("Data received")
            except OSError as os_err:
                print(f'Something went wrong: {os_err}')
                break

            # if empty exit
            if not data_received:
                debugger("Empty received data")
                break
            debugger("Length of received data:", len(data_received))

            # parsing data
            try:
                query.parse(data_received)
            except ValueError as err:
                debugger("Parsing error")
                print(f'Something went wrong: {err}')
                continue
            debugger("Query:", query.print())

            # checking if session is correct
            if query.session_id != session_id:
                if session_id == -1:
                    # first time receiving
                    debugger("Session_id unset, saving session id")
                    session_id = query.session_id
                else:
                    # wrong session
                    debugger("Wrong session id")
                    self.request.send(GENERAL_ERROR.pack())
                    continue

            # checking if client want to calculate
            if query.status is not 1:
                debugger("Wrong status number")
                error_packet = STATUS_ERROR
                error_packet.session_id = query.session_id
                self.request.send(error_packet.pack())
                continue
            else:
                debugger("Status 1, calculating")

                # response will be only one argument
                #  unless the operation is not or factorial
                query.set_length(False)

                if query.operation == OPERATORS[0]:
                    query.first = query.first + query.second
                elif query.operation == OPERATORS[1]:
                    query.first = query.first - query.second
                elif query.operation == OPERATORS[2]:
                    query.first = query.first * query.second
                elif query.operation == OPERATORS[3]:
                    if query.second == 0:
                        errors = 7
                    else:
                        query.first = int(query.first / query.second)
                elif query.operation == OPERATORS[4]:
                    query.first = int(query.first % query.second)
                elif query.operation == OPERATORS[5]:
                    query.first = int(pow(query.first, query.second))
                elif query.operation == OPERATORS[6]:
                    query.first = int(log(query.second, query.first))
                elif query.operation == OPERATORS[7]:
                    # unless the operation is abs or factorial
                    if query.first > 0:
                        query.second = factorial(query.first)
                        query.set_length(True)
                    else:
                        errors = 6
                    query.first = int(fabs(query.first))

                # checking if result isn't too big or too small
                if query.first > MAX_INT:
                    debugger("Result too big for 32bit int")
                    errors = 4
                if query.first < MIN_INT:
                    debugger("Result too small for 32bit int")
                    errors = 4
                if query.second > MAX_INT:
                    debugger("Factorial too big for 32bit int")
                    errors = 6
                if query.second < MIN_INT:
                    debugger("Factorial too small for 32bit int")
                    errors = 6

                # if there is no errors prepare query
                if errors == 0:
                    debugger("No errors, sending")
                    query.status = 2

                elif errors == 4:
                    # otherwise handle errors
                    debugger(f"Error code:", errors)
                    query.status = 4
                    query.first = 0
                    query.second = 0
                    query.set_length(False)
                    # send error
                    debugger("Error response:", query.print())

                elif errors == 6:
                    # otherwise handle errors
                    debugger(f"Error code:", errors)
                    query.status = 6
                    query.second = 0
                    query.set_length(False)
                    # send error
                    debugger("Error response:", query.print())

                elif errors == 7:
                    # otherwise handle errors
                    debugger(f"Error code:", errors)
                    query.status = 7
                    query.first = 0
                    query.second = 0
                    query.set_length(False)
                    # send error
                    debugger("Error response:", query.print())

                debugger("Length of prepared response:", len(query.pack()))
                debugger("Response:", query.print())

                try:
                    self.request.sendall(query.pack())
                except OSError as err:
                    print(f'Something went wrong: {os_err}')
                    break

        debugger("Handled")
        print("Disconnected")


if __name__ == "__main__":
    args = sys.argv
    host = args[1] if len(args) > 1 else HOST
    port = int(args[2]) if len(args) > 2 else PORT
    forever = bool(args[3]) if len(args) > 3 else DEBUG
    with socketserver.TCPServer((host, port), TurboProtocolTCPHandler) as server:
        print("Server started")
        if forever:
            server.serve_forever()
        else:
            server.handle_request()
    input("Press ENTER to continue...")
    sys.exit()
