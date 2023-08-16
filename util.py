from bitarray import bitarray


def generate_packet(address: int, data: bitarray) -> bytearray:
    packet = bytearray(b"\x02" + encode_byte(address + 17))
    packet += encode_byte(len(data) // 8)
    data_bytes = data.tobytes()
    for value in data_bytes:
        packet += encode_byte(value)
    csum = checksum(packet)
    packet += b"\x03" + encode_byte(csum)
    return packet


def encode_byte(value: int) -> bytes:
    """ Protocol encodes each byte as an uppercase, ASCII representation of the
        hex value. So, one input byte becomes two output bytes.
    """
    assert value < 256
    return "{:02X}".format(value).encode('ascii')


def checksum(data: bytes) -> int:
    csum = sum(data)

    # Start of text (0x02) must be removed,
    # End of text (0x03) must be added
    csum += 1

    # Result must be casted to 8 bits
    csum = csum & 0xFF

    # Checksum is the sum XOR 255 + 1. So, sum of all bytes + checksum
    # is equal to 0 (8 bits)
    csum = (csum ^ 255) + 1

    csum = csum & 0xFF

    return csum
