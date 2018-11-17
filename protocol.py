from struct import pack, unpack
from bitstring import BitArray


DEBUG = False


class Turbo:

    # offset
    offset = BitArray(uint=0, length=1)

    # length of data
    length = 32*3

    # header and data wrappers
    header = ''
    data = ''

    def __init__(self, operation="+", status=0, session_id=100, extendedarguments=True, first=0, second=0):
        self.operation = operation
        self.status = status
        self.session_id = session_id
        self.first = first
        self.second = second
        self.extendedArguments = extendedarguments

        # packing after init
        self.pack_packet()

    def pack_data(self):
        if not self.extendedArguments:
            self.data = pack("!ii", self.session_id, self.first)
        else:
            self.data = pack("!iii", self.session_id, self.first, self.second)

    def unpack_data(self):
        if not self.extendedArguments:
            data = unpack("!ii", self.data)
            self.session_id = data[0]
            self.first = data[1]
            self.second = 0
        else:
            data = unpack("!iii", self.data)
            self.session_id = data[0]
            self.first = data[1]
            self.second = data[2]

    def pack_packet(self):
        self.pack_data()

        # converting operation to bits
        if self.operation == '+':
            operation = BitArray(uint=0, length=3)
        elif self.operation == '-':
            operation = BitArray(uint=1, length=3)
        elif self.operation == '*':
            operation = BitArray(uint=2, length=3)
        elif self.operation == '/':
            operation = BitArray(uint=3, length=3)
        elif self.operation == 'OR':
            operation = BitArray(uint=4, length=3)
        elif self.operation == 'XOR':
            operation = BitArray(uint=5, length=3)
        elif self.operation == 'AND':
            operation = BitArray(uint=6, length=3)
        elif self.operation == 'NOT':
            operation = BitArray(uint=7, length=3)
        elif self.operation == '!':
            operation = BitArray(uint=7, length=3)
        else:
            raise Exception(f'Wrong operation character: {self.operation}')

        # converting status to bits
        status = BitArray(int=self.status, length=4)
        if not self.extendedArguments:
            self.length = 64
        else:
            self.length = 96

        # assembling header
        header = operation + status + BitArray(int=self.length, length=32) + self.offset
        self.header = header.bytes

        # assembling packet
        packet = self.header + self.data
        if DEBUG:
            print("packet:", packet)
        return packet

    def parse_data(self, data):
        self.data = BitArray(data)
        header = self.data[0:40]
        self.data = self.data[40:].bytes

        if DEBUG:
            print("header + data:", header.bin, data)
            print("header values:", header[0:3].uint, header[3:7].uint, header[7:-1].int, int(header[-1]))

        operation = header[0:3].uint
        self.status = header[3:7].int
        self.length = header[7:-1].int
        if self.length == 96:
            self.extendedArguments = True
        elif self.length == 64:
            self.extendedArguments = False
        else:
            raise Exception("Unknown length")

        if operation == 0:
            self.operation = '+'
        elif operation == 1:
            self.operation = '-'
        elif operation == 2:
            self.operation = '*'
        elif operation == 3:
            self.operation = '/'
        elif operation == 4:
            self.operation = 'OR'
        elif operation == 5:
            self.operation = 'XOR'
        elif operation == 6:
            self.operation = 'AND'
        elif operation == 7:
            self.operation = 'NOT'

        self.unpack_data()

    def print(self):
        if DEBUG:
            print(self.operation, self.status, self.session_id, self.extendedArguments, self.first, self.second)
        return str(f"{self.operation}, {self.status}, {self.session_id}, {self.extendedArguments}, {self.first}, {self.second}")


def main():
    # only for testing
    f_packet = Turbo("/", 7, 1997, True,  -2147483648, 2147483647)
    f_packet.print()

    s_packet = Turbo()
    print(len(f_packet.pack_packet()))
    s_packet.parse_data(f_packet.pack_packet())
    print(len(s_packet.pack_packet()))
    s_packet.print()

    s_packet.extendedArguments = False
    print("***")
    print(len(s_packet.pack_packet()))
    s_packet.print()

    f_packet.parse_data(s_packet.pack_packet())
    f_packet.print()


if __name__ == "__main__":
    main()
