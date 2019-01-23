import struct


# The file begins with eight magic bytes
_header_magic = b'farbfeld'

# Following the magic bytes are width and
# height as 32-bit unsigned big-endian integers.
_header_struct = struct.Struct('>8s2L')

# After that are pixel components (RGBA),
# each being 16-bit unsigned big-endian integers.
_pixel_struct = struct.Struct('>4H')


class InvalidFormat(Exception):
    pass


def _read_header(data):
    # Unpack header
    header = data[:_header_struct.size]
    try:
        magic, width, height = _header_struct.unpack(header)
    except struct.error:
        raise InvalidFormat('invalid header format')

    # Make sure it's a farbfeld file
    if magic != _header_magic:
        raise InvalidFormat('invalid header signature')

    return width, height


def _read_pixels(buffer, width, height):
    rows = []
    column = []
    offset = 0
    num_bytes = width * height * _pixel_struct.size
    while offset < num_bytes:
        rgba = _pixel_struct.unpack_from(buffer, offset)
        column.append(list(rgba))
        if len(column) >= width:
            rows.append(column)
            column = []
        offset += _pixel_struct.size
    return rows


def read(data):
    """
    Reads the given raw image data (for example the contents of a file)
    and returns the corresponding pixels as a list. The list contains
    another list for each row of the image, and each nested list contains
    the pixels on that row as a list [r, g, b, a].

    :param data: bytes to read as an image.
    :return: list of pixels
    :rtype: list
    """
    width, height = _read_header(data)
    pixel_data = data[_header_struct.size:]
    pixels = _read_pixels(pixel_data, width, height)
    return pixels
