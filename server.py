import socketserver
from protocol import Turbo
from math import factorial
import copy

DEBUG = True
MAX_INT = 2147483647
MIN_INT = -2147483648

GENERAL_ERROR = Turbo("+", 3, 0, False, 0, 0)
SIZE_ERROR = Turbo("+", 4, 0, False, 0, 0)
STATUS_ERROR = Turbo("+", 5, 0, False, 0 ,0)


def debugger(msg):
    if DEBUG:
        print("DEBUG:", msg)


class TurboProtocolTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        debugger("Handle")
        print("Connected")
        packet = Turbo()
        errors = 0
        session_id = -1

        while True:
            try:
                data = self.request.recv(1024)
            except OSError as msg:
                print(f'Something went wrong: {msg.strerror}, code: [{msg.errno}], address: {self.client_address}')
                self.request.close()
                break

            if not data:
                debugger("Empty data")
                break

            packet = packet.parse_data(data)

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
                packet.extendedArgument = False

                if packet.operation == '+':
                    packet.first = packet.first + packet.second
                elif packet.operation == '-':
                    packet.first = packet.first - packet.second
                elif packet.operation == '*':
                    packet.first = packet.first * packet.second
                elif packet.operation == '/':
                    packet.first = int(packet.first / packet.second)
                elif packet.operation == 'OR':
                    packet.first = packet.first | packet.second
                elif packet.operation == 'XOR':
                    packet.first = packet.first ^ packet.second
                elif packet.operation == 'AND':
                    packet.first = packet.first & packet.second
                elif packet.operation == 'NOT':
                    packet.first = ~packet.first
                    packet.second = factorial(packet.second)
                    # unless the operation is logic not or factorial
                    packet.extendedArgument = True

                # checking if result isnt too big or too small
                if packet.first > MAX_INT or packet.second > MAX_INT:
                    debugger("Result too big for 32bit int")
                    errors += 1
                if packet.first < MIN_INT or packet.second < MIN_INT:
                    debugger("Result too small for 32bit int")
                    errors += 1

                # if there is no errors send packet
                if errors == 0:
                    packet.status = 2
                    old_packet = copy.copy(packet)
                    self.request.send(packet.pack_packet())
                else:
                    # otherwise handle errors
                    debugger(f"Errors: {errors}")
                    packet.status = 4
                    packet.first = 0
                    packet.second = 0
                    packet.extendedArgument = False
                    # send error
                    old_packet = copy.copy(packet)
                    self.request.send(packet.pack_packet())

        debugger("Handled")
        print("Disconnected")


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    with socketserver.TCPServer((HOST, PORT), TurboProtocolTCPHandler) as server:
        print("Server started")
        server.serve_forever()
