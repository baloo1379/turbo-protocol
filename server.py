import socketserver
from protocol import Turbo


DEBUG = True


class TurboProtocolTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        if DEBUG:
            print("Handle")

        data = self.request.recv(1024)
        word = data.decode()
        if word is None:
            return
        word = word.upper()
        print(word)
        self.request.sendall(word.encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    with socketserver.TCPServer((HOST, PORT), TurboProtocolTCPHandler) as server:
        print("Server started")
        server.serve_forever(5.0)
