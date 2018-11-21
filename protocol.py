from struct import pack, unpack
from bitstring import BitArray


DEBUG = False
OPERATORS = ["+", "-", "*", "/", "%", "^", "log", "abs", "!"]


def debugger(*msgs):
    if DEBUG:
        result = "DEBUG:"
        for el in msgs:
            result += " "+str(el)
        print(result)


class Turbo:

    # offset
    offset = BitArray(uint=0, length=1)

    # header and data wrappers
    header = ''
    data = ''
    bytes = b''

    def __init__(self, operation="+", status=0, session_id=100, second_argument=True, first=0, second=0):
        self.operation = operation
        self.status = status
        self.session_id = session_id
        self.first = first
        self.second = second
        self.length = 64
        self.second_argument = second_argument
        self.set_length(self.second_argument)
        self.pack()

    def set_length(self, value: bool):
        self.second_argument = value
        if not self.second_argument:
            self.length = 64
        else:
            self.length = 96

    def pack_data(self):
        if not self.second_argument:
            self.data = BitArray(bytes=pack("!ii", self.session_id, self.first), length=64)
        else:
            self.data = BitArray(bytes=pack("!iii", self.session_id, self.first, self.second), length=96)

    def unpack_data(self, data: bytes):
        if not self.second_argument:
            data = unpack("!ii", data)
            self.session_id = data[0]
            self.first = data[1]
            self.second = 0
        else:
            data = unpack("!iii", data)
            self.session_id = data[0]
            self.first = data[1]
            self.second = data[2]
        return self.session_id, self.first, self.second

    def pack(self):
        # packing data
        self.pack_data()

        # converting operation to bits
        if self.operation == OPERATORS[0]:
            operation = BitArray(uint=0, length=3)
        elif self.operation == OPERATORS[1]:
            operation = BitArray(uint=1, length=3)
        elif self.operation == OPERATORS[2]:
            operation = BitArray(uint=2, length=3)
        elif self.operation == OPERATORS[3]:
            operation = BitArray(uint=3, length=3)
        elif self.operation == OPERATORS[4]:
            operation = BitArray(uint=4, length=3)
        elif self.operation == OPERATORS[5]:
            operation = BitArray(uint=5, length=3)
        elif self.operation == OPERATORS[6]:
            operation = BitArray(uint=6, length=3)
        elif self.operation == OPERATORS[7]:
            operation = BitArray(uint=7, length=3)
        elif self.operation == OPERATORS[8]:
            operation = BitArray(uint=7, length=3)
        else:
            raise ValueError(f'Wrong operation sign: {self.operation}')

        # converting status to bits
        status = BitArray(int=self.status, length=4)

        # calculating length
        if not self.second_argument:
            self.length = 64
        else:
            self.length = 96
        length = BitArray(int=self.length, length=32)

        # assembling header
        header = operation + status + length

        # assembling query
        debugger("assembling query", operation.int, status.int, length.int, self.unpack_data(self.data.tobytes()), self.offset.int)
        bit_packet = header + self.data + self.offset
        packet = bit_packet.tobytes()
        self.bytes = packet
        debugger("query  ", packet)
        return packet

    def parse(self, raw_data: bytes):
        # converting bytes into BitArray
        bit_data = BitArray(raw_data)
        debugger("payload ", bit_data.bin, len(bit_data.bin), "bits")

        # trim header and data
        header = bit_data[0:39]
        data = bit_data[39:-1]
        debugger("header  ", header.bin, len(header.bin), "bits")
        debugger("data    ", data.bin, len(data.bin), "bits")

        # parse header
        operation = header[0:3].uint
        status = header[3:7].int
        length = header[7:].int

        # set length
        if length == 96:
            self.set_length(True)
        elif length == 64:
            self.set_length(False)
        else:
            raise ValueError("Unknown length")

        # set operation
        if operation == 0:
            self.operation = OPERATORS[0]
        elif operation == 1:
            self.operation = OPERATORS[1]
        elif operation == 2:
            self.operation = OPERATORS[2]
        elif operation == 3:
            self.operation = OPERATORS[3]
        elif operation == 4:
            self.operation = OPERATORS[4]
        elif operation == 5:
            self.operation = OPERATORS[5]
        elif operation == 6:
            self.operation = OPERATORS[6]
        elif operation == 7:
            self.operation = OPERATORS[7]
        else:
            raise ValueError(f'Wrong operation sign')

        # set status
        self.status = status

        # unpacking and setting data
        self.unpack_data(data.tobytes())

    def print(self):
        return str(f"{self.operation}, {self.status}, {self.length}, {self.session_id}, {self.second_argument}, "
                   f"{self.first}, {self.second}")


def main():
    # only for testing
    x = Turbo("+", 7, 1997, True, 564, 85), Turbo("-", 7, 1997, True, 452, 654), Turbo("*", 7, 1997, True, 15, 5), \
        Turbo("/", 7, 1997, True, 25, 5), Turbo("%", 7, 1997, True, 25, 6), Turbo("^", 7, 1997, True, 2, 8), \
        Turbo("log", 7, 1997, True, 3, 8), Turbo("abs", 7, 1997, False, 25, 0), Turbo("abs", 7, 1997, True, 0, 5)

    packet = Turbo()
    for el in x:
        proto_bytes = el.pack()
        try:
            packet.parse(proto_bytes)
        except ValueError as err:
            print(err)
        else:
            print(packet.print())


def translate():
    data = input()
    str_data = data.split(",")
    print(str_data)
    raw_data = list()
    for el in str_data:
        raw_data.append(int(el[3:], 16))
    x = bytes(raw_data)
    print(x)
    packet = Turbo()
    packet.parse(x)
    print(packet.print())


if __name__ == "__main__":
    DEBUG = True
    main()
