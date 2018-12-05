from bitstring import BitArray


DEBUG = True
OPERATORS = ["+", "-", "*", "/", "%", "^", "log", "abs", "!"]
MAX_INT = int(9223372036854775807)
MIN_INT = int(-9223372036854775808)
padding = 20


def debugger(*msgs):
    if DEBUG:
        result = "DEBUG:"
        for el in msgs:
            result += " "+str(el)
        print(result)


def str_padded(msg: str):
    global padding
    if len(msg) > padding:
        padding = len(msg)
    for el in range(padding-len(msg)):
        msg += "."
    return msg


class Turbo:

    def __init__(self, operation="+", status=0, session_id=0, first=0, second=0, parse=b''):
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

        if parse:
            self.parse(parse)
        else:
            self.pack()

    @staticmethod
    def pack_field(value):
        debugger("** packing field **")
        if value == 0:
            debugger("value empty")
            value_flag = BitArray(uint=0, length=1)
            value_length = 1
            debugger("** field packed **")
            return value_flag, value_length
        else:
            value_flag = BitArray(uint=1, length=1)
            debugger(str_padded("value length"), value.bit_length())
            if value.bit_length() < 16:
                value_length = 16
            elif value.bit_length() < 32:
                value_length = 32
            elif value.bit_length() <= 64:
                value_length = 64
            else:
                debugger(str_padded("value too big"), value.bit_length())
                raise OverflowError

            debugger(str_padded("value bits"), value_length)

            total_length = 1 + 8 + value_length

            value_array = BitArray(int=value, length=value_length)
            value_length = BitArray(uint=value_length, length=8)

            debugger("** field packed **")
            return value_flag, value_length, value_array, total_length

    def pack_data(self, elements: tuple):
        debugger("---- packing data ----")
        self.data = BitArray(length=0)
        self.length = 0
        for el in elements:
            temp = self.pack_field(el)
            self.length += temp[-1]
            for fl in temp[:-1]:
                self.data += fl

        debugger(str_padded("data"), self.data.bin)
        debugger(str_padded("length"), self.length)
        debugger("---- data packed ----")

    @staticmethod
    def unpack_data(data: bytes):
        debugger("== unpacking data ==")
        bin_data = BitArray(data)
        result = list()

        for el in range(3):
            field_ex = bin_data[0]
            bin_data = bin_data[1:]
            if not field_ex:
                field = 0
            else:
                field_length = bin_data[0:8].uint
                debugger(str_padded(f"field {el} len"), field_length)
                bin_data = bin_data[8:]
                field = bin_data[0:field_length].int
                bin_data = bin_data[field_length:]
            result.append(field)
            debugger(str_padded(f"field {el}"), field)

        debugger("== data unpacked ==")
        return tuple(result)

    def pack(self):
        debugger("## main pack ##")
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
        offset = 8 - (39 + self.length) % 8
        debugger(str_padded("offset"), offset)
        length = BitArray(uint=self.length+offset, length=32)

        # assembling header
        header = operation + status + length

        # assembling query
        debugger(str_padded("assembling query"), operation.uint, status.uint, length.uint,
                 self.unpack_data(self.data.tobytes()))
        bit_packet = header + self.data
        debugger(str_padded("query bits"), bit_packet.bin, len(bit_packet.bin), "bits")
        packet = bit_packet.tobytes()
        self.bytes = packet
        debugger("## packed ##")
        return packet

    def parse(self, raw_data: bytes):
        # converting bytes into BitArray
        bit_data = BitArray(raw_data)
        debugger(str_padded("payload"), bit_data.bin, len(bit_data.bin), "bits")

        # trim header and data
        header = bit_data[0:39]
        data = bit_data[39:]
        debugger(str_padded("header"), header.bin, len(header.bin), "bits")
        debugger(str_padded("data"), data.bin, len(data.bin), "bits")

        # parse header
        operation = header[0:3].uint
        header = header[3:]
        status = header[0:4].uint
        header = header[4:]
        length = header.uint

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
            raise ValueError("Wrong operation sign")

        # set status
        self.status = status

        # set length
        self.length = length

        # unpacking and setting data
        self.session_id, self.first, self.second = self.unpack_data(data.tobytes())

    def print(self):
        return str(f"{self.operation}, {self.status}, {self.length}, {self.session_id}, {self.first}, {self.second}")


def main():
    # only for testing

    x = Turbo("+", 7, 100, 0, 0), Turbo("-", 7, 101, 1, 0), Turbo("*", 7, 102, 1, 1), \
        Turbo("/", 7, 103, 256, 70000000), Turbo("%", 7, 104, 131071, 17592186044415), Turbo("^", 7, 105, 2, 8), \
        Turbo("log", 7, 106, 3, 8), Turbo("abs", 7, 107, 25, 0), Turbo("abs", 7, 108, 0, 5)

    packet = x[3]
    print()
    packet.parse(packet.pack())


def translate():
    data = input()
    bin_data = BitArray(hex=data)
    print(bin_data.bin)

    packet = Turbo(parse=bin_data.tobytes())
    print(packet.print())


if __name__ == "__main__":
    main()
