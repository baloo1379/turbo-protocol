import socketserver
from protocol import Turbo


DEBUG = True


def debugger(msg):
    if DEBUG:
        print("DEBUG:", msg)


class TurboProtocolTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        debugger("Handle")
        print("Connected")
        protocol = Turbo()

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

            protocol = protocol.parse_data(data)
            word = word.upper()
            print(word)
            self.request.sendall(word.encode())

        debugger("Handled")
        print("Disconnected")


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    with socketserver.TCPServer((HOST, PORT), TurboProtocolTCPHandler) as server:
        print("Server started")
        server.serve_forever()
