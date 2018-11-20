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
        debugger("handle entered")
        print("Connected with", socket.gethostbyaddr(self.client_address[0])[0], "from", self.client_address[0],
              "on port", self.client_address[1])
        packet = Turbo()
        session_id = -1

        while True:
            debugger("waiting for client")
            try:
                data = self.request.recv(8192)
                debugger("data received")
            except OSError as msg:
                print(f'Something went wrong: {msg.strerror}, code: [{msg.errno}], address: {self.client_address}')
                self.request.close()
                break

            if not data:
                debugger("empty data")
                break

            errors = 0
            old_packet = copy.copy(packet)
            debugger("length of raw data:", str(len(data)))
            try:
                packet.parse_data(data)
            except ValueError as msg:
                debugger("parsing error")
                print(f'Something went wrong: {msg}')
                continue

            debugger("packet:", packet.print())

            # checking if session is correct
            if packet.session_id != session_id:
                if session_id == -1:
                    # first time receiving
                    debugger("Session_id unset. Saving session id")
                    session_id = packet.session_id
                else:
                    # wrong session
                    debugger("Wrong session id")
                    self.request.send(GENERAL_ERROR.pack_packet())
                    continue

            # checking if client want to calculate
            if packet.status is not 1:
                debugger("Wrong status number")
                error_packet = STATUS_ERROR
                error_packet.session_id = packet.session_id
                self.request.send(error_packet.pack_packet())
                continue
            else:
                debugger("Status 1, calculating")

                # response will be only one argument
                #  unless the operation is not or factorial
                packet.set_length(False)

                if packet.operation == OPERATORS[0]:
                    packet.first = packet.first + packet.second
                elif packet.operation == OPERATORS[1]:
                    packet.first = packet.first - packet.second
                elif packet.operation == OPERATORS[2]:
                    packet.first = packet.first * packet.second
                elif packet.operation == OPERATORS[3]:
                    if packet.second == 0:
                        errors = 7
                    else:
                        packet.first = int(packet.first / packet.second)
                elif packet.operation == OPERATORS[4]:
                    packet.first = int(packet.first % packet.second)
                elif packet.operation == OPERATORS[5]:
                    packet.first = int(pow(packet.first, packet.second))
                elif packet.operation == OPERATORS[6]:
                    packet.first = int(log(packet.second, packet.first))
                elif packet.operation == OPERATORS[7]:
                    # unless the operation is abs or factorial
                    if packet.first > 0:
                        packet.second = factorial(packet.first)
                        packet.set_length(True)
                    else:
                        errors = 6
                    packet.first = int(fabs(packet.first))

                # checking if result isn't too big or too small
                if packet.first > MAX_INT:
                    debugger("Result too big for 32bit int")
                    errors = 4
                if packet.first < MIN_INT:
                    debugger("Result too small for 32bit int")
                    errors = 4
                if packet.second > MAX_INT:
                    debugger("Factorial too big for 32bit int")
                    errors = 6
                if packet.second < MIN_INT:
                    debugger("Factorial too small for 32bit int")
                    errors = 6

                # if there is no errors prepare packet
                if errors == 0:
                    debugger("No errors. Sending")
                    packet.status = 2
                    old_packet = copy.copy(packet)
                    debugger(packet.extendedArguments)
                    debugger(packet.length)

                elif errors == 4:
                    # otherwise handle errors
                    debugger(f"Errors code:", errors)
                    packet.status = 4
                    packet.first = 0
                    packet.second = 0
                    packet.set_length(False)
                    # send error
                    old_packet = copy.copy(packet)
                    debugger("error packet:", packet.print(), packet.pack_packet())

                elif errors == 6:
                    # otherwise handle errors
                    debugger(f"Errors code:", errors)
                    packet.status = 6
                    packet.second = 0
                    packet.set_length(False)
                    # send error
                    old_packet = copy.copy(packet)
                    debugger("error packet:", packet.print(), packet.pack_packet())

                elif errors == 7:
                    # otherwise handle errors
                    debugger(f"Errors code:", errors)
                    packet.status = 7
                    packet.first = 0
                    packet.second = 0
                    packet.set_length(False)
                    # send error
                    old_packet = copy.copy(packet)
                    debugger("error packet:", packet.print(), packet.pack_packet())

                debugger("len: " + str(len(packet.pack_packet())))
                debugger("send packet:", packet.print())
                self.request.sendall(packet.pack_packet())

        debugger("Handled")
        print("Disconnected")


if __name__ == "__main__":
    args = sys.argv
    host = args[1] if len(args) > 1 else HOST
    port = int(args[2]) if len(args) > 2 else PORT
    forever = bool(args[3]) if len(args) > 3 else False
    with socketserver.TCPServer((host, port), TurboProtocolTCPHandler) as server:
        print("Server started")
        if forever:
            server.serve_forever()
        else:
            server.handle_request()
    input("Press ENTER to continue...")
    sys.exit()
