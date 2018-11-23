from bitstring import BitArray


DEBUG = False
OPERATORS = ["+", "-", "*", "/", "%", "^", "log", "abs", "!"]
MAX_INT = int(9223372036854775807)
MIN_INT = int(-9223372036854775808)


def debugger(*msgs):
    if DEBUG:
        result = "DEBUG:"
        for el in msgs:
            result += " "+str(el)
        print(result)


class Turbo:

    def __init__(self, operation="+", status=0, session_id=100, first=0, second=0):
        self.operation = operation
        self.status = int(status)
        self.session_id = int(session_id)
        self.first = int(first)
        self.second = int(second)
        self.length = 0
        self.data = BitArray(length=0)
        self.header = BitArray(length=0)
        self.offset = BitArray(uint=0, length=1)
        self.bytes = b''

        self.pack()

    @staticmethod
    def pack_field(value):
        debugger("packing field")
        if value == 0:
            debugger("value empty")
            value_flag = BitArray(uint=0, length=1)
            value_length = 1
            debugger("field packed")
            return value_flag, value_length
        else:
            value_flag = BitArray(uint=1, length=1)
            debugger("value length", value.bit_length())
            if value.bit_length() < 16:
                value_length = 16
            elif value.bit_length() < 32:
                value_length = 32
            elif value.bit_length() <= 64:
                value_length = 64
            else:
                debugger("value too big", value.bit_length())
                raise OverflowError

            debugger("value bits", value_length)

            total_length = 1 + 8 + value_length

            value_array = BitArray(int=value, length=value_length)
            value_length = BitArray(uint=value_length, length=8)

            debugger("field packed")
            return value_flag, value_length, value_array, total_length

    def pack_data(self, elements):
        debugger("packing data")
        for el in elements:
            temp = self.pack_field(el)
            debugger(temp, temp[-1], temp[:-1])
            self.length += temp[-1]
            for fl in temp[:-1]:
                debugger(fl.bin)
                self.data += fl

        debugger("data", self.data.bin)
        debugger("length", self.length)
        debugger("data packed")

    # deprecated
    # def unpack_data(self, data: bytes):
    #     if not self.second_argument:
    #         data = unpack("!ii", data)
    #         self.session_id = data[0]
    #         self.first = data[1]
    #         self.second = 0
    #     else:
    #         data = unpack("!iii", data)
    #         self.session_id = data[0]
    #         self.first = data[1]
    #         self.second = data[2]
    #     return self.session_id, self.first, self.second

    def pack(self):
        # packing data
        self.pack_data((self.session_id, self.first, self.second))

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
        status = BitArray(uint=self.status, length=4)

        # calculating length
        # if not self.second_argument:
        #     self.length = 64
        # else:
        #     self.length = 96
        length = BitArray(uint=self.length, length=32)

        # assembling header
        header = operation + status + length

        # assembling query
        debugger("assembling query", operation.int, status.int, length.int, self.data.bin)
        bit_packet = header + self.data
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
        status = header[3:7].uint
        length = header[7:].uint

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
    x = Turbo("+", 7, MAX_INT, MIN_INT, MIN_INT)

    # x = Turbo("+", 7, 100, 0, 0), Turbo("-", 7, 1997, 1, 0), Turbo("*", 7, 1997, 1, 1), \
    #     Turbo("/", 7, 1997, 256, 70000000), Turbo("%", 7, 1997, 25, 6), Turbo("^", 7, 1997, 2, 8), \
    #     Turbo("log", 7, 1997, 3, 8), Turbo("abs", 7, 1997, 25, 0), Turbo("abs", 7, 1997, 0, 5)

    # packet = Turbo()
    # for el in x:
    #     proto_bytes = el.pack()
    #     try:
    #         packet.parse(proto_bytes)
    #     except ValueError as err:
    #         print(err)
    #     else:
    #         print(packet.print())


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
