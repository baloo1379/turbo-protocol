import socketserver
from protocol import Turbo


DEBUG = True


class TurboProtocolTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        if DEBUG:
            print("Handle")

        data = self.request.recv(4096)
        word = data.decode()
        if word == "":
            return
        word = word.upper()
        print(word)
        self.request.sendall(word.encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    with socketserver.TCPServer((HOST, PORT), TurboProtocolTCPHandler) as server:
        print("Server started")
        server.serve_forever(5.0)
