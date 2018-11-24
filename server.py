import socketserver
import socket
import sys
from math import factorial, pow, log, fabs
from protocol import Turbo, OPERATORS, MIN_INT, MAX_INT


DEBUG = False

HOST, PORT = "localhost", 9999

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
                data_received = self.request.recv(512)
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
                result = 0
                result2 = 0
                operation = query.operation

                if operation == OPERATORS[0]:
                    result = query.first + query.second
                elif operation == OPERATORS[1]:
                    result = query.first - query.second
                elif operation == OPERATORS[2]:
                    result = query.first * query.second
                elif operation == OPERATORS[3]:
                    if query.second == 0:
                        errors = 7
                    else:
                        result = int(query.first / query.second)
                elif operation == OPERATORS[4]:
                    result = int(query.first % query.second)
                elif operation == OPERATORS[5]:
                    try:
                        result = int(pow(query.first, query.second))
                    except OverflowError as err:
                        errors = 4
                elif operation == OPERATORS[6]:
                    try:
                        result = int(log(query.second, query.first))
                    except ValueError as err:
                        errors = 8
                elif operation == OPERATORS[7]:
                    # unless the operation is abs or factorial
                    if query.first > 0:
                        result2 = factorial(query.first)
                    else:
                        errors = 6
                        result = int(fabs(query.first))

                # checking if result isn't too big or too small
                if result > MAX_INT:
                    debugger("Result too big for 32bit int")
                    errors = 4
                if result < MIN_INT:
                    debugger("Result too small for 32bit int")
                    errors = 4
                if result2 > MAX_INT:
                    debugger("Factorial too big for 32bit int")
                    errors = 6
                if result2 < MIN_INT:
                    debugger("Factorial too small for 32bit int")
                    errors = 6

                # if there is no errors prepare query
                # otherwise handle error
                if errors == 0:
                    debugger("No errors, sending")
                    status = 2

                elif errors == 6:
                    # factorial too big
                    debugger(f"Error code:", errors)
                    status = 6
                    result2 = 0

                else:
                    debugger(f"Error code:", errors)
                    status = errors
                    result = 0
                    result2 = 0

                # elif errors == 7:
                #     # division by 0
                #     debugger(f"Error code:", errors)
                #     status = errors
                #     result = 0
                #     result2 = 0
                #
                # elif errors == 8:
                #     # logarithm
                #     debugger(f"Error code:", errors)
                #     status = errors
                #     result = 0
                #     result2 = 0

                response = Turbo(operation, status, session_id, result, result2)
                debugger("Length of prepared response:", len(response.pack()))
                debugger("Response:", response.print())

                try:
                    self.request.sendall(response.pack())
                except OSError as os_err:
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
