"""
Module for working with the farbfile image format.

This module can be used to read pixel data from farbfeld image files.
The image format consists of the bytes 'farbfeld' followed by the
image width and height as 32-bit unsigned big-endian integers. After
these, the actual image data is of length width*height and consists
of four-component (RGBA) pixels, each component being 16-bit unsigned
big-endian integers.

To read a farbfile image:

>>> with open('image.ff', 'rb') as f:
...     data = read(f)

This will return the pixels as a nested list: the first list contains
the pixels on the first row, the second list contains the second row,
and so on. Each pixels is in turn a list containing four components.

Note that the pixel components are 16-bit unsigned integers, so the
values are between 0 and 65535. You can scale them to the [0, 1]
range by using the 'normalize' argument:

>>> with open('image.ff', 'rb') as f:
...     data = read(f, normalize=True)
"""

import struct


# The file begins with eight magic bytes
HEADER_MAGIC = b'farbfeld'

# Following the magic bytes are width and
# height as 32-bit unsigned big-endian integers.
HEADER_STRUCT = struct.Struct('>8s2L')

# After that are pixel components (RGBA),
# each being 16-bit unsigned big-endian integers.
PIXEL_STRUCT = struct.Struct('>4H')

# Since each component is 16-bits, this is the maximum value
COMPONENT_MAX = 2**16 - 1


class InvalidFormat(Exception):
    """
    Raised if the file header is invalid, or the file
    is otherwise formatted in an invalid way.
    """


def _read_header(data):
    """
    Extracts the header part from the given data, validates it,
    and returns the image width and height based on it.

    :param data: image data.
    :type data: typing.BinaryIO
    :return: tuple containing the image width and height.
    :rtype: (int, int)
    """
    # Unpack header
    try:
        header = data.read(HEADER_STRUCT.size)
        magic, width, height = HEADER_STRUCT.unpack(header)
    except struct.error:
        raise InvalidFormat('invalid header format')

    # Make sure it's a farbfeld file
    if magic != HEADER_MAGIC:
        raise InvalidFormat('invalid header signature')

    return width, height


def _normalize_pixels(pixels):
    """
    Scales the components of given pixels to the range [0, 1].

    :param pixels: pixels to scale
    :type pixels: list
    """
    for i, pixel in enumerate(pixels):
        pixels[i] = [component / COMPONENT_MAX for component in pixel]


def _read_pixels(buffer, count):
    """
    Unpacks pixels from the given buffer.

    :param buffer: raw pixel data to read from.
    :type buffer: typing.BinaryIO
    :param count: number of pixels to read
    :type count: int
    :return: pixel data as a nested list.
    :rtype: list
    """
    pixels = []
    try:
        # Unpack the buffer pixel by pixel
        for rgba in PIXEL_STRUCT.iter_unpack(buffer.read()):
            pixels.append(list(rgba))
    except struct.error:
        # Some components are missing
        raise InvalidFormat("incomplete pixels")

    # Make sure we got the correct amount of pixels
    if len(pixels) != count:
        raise InvalidFormat("number of pixels does not match header")

    return pixels


def _group_pixels(pixels, num_rows):
    """
    Group the given pixels into a nested list containing rows of pixels.

    :param pixels:
    :param num_rows: Number of rows in each
    :return: pixels grouped by row
    """
    offset = 0
    rows = []
    while offset < len(pixels):
        rows.append(pixels[offset:offset + num_rows])
        offset += num_rows
    return rows


def read(data, normalize=False):
    """
    Reads the given raw image data (for example the contents of a file)
    and returns the corresponding pixels as a list. The list contains
    another list for each row of the image, and each nested list contains
    the pixels on that row as a list [r, g, b, a].

    Optionally, the pixel components can be normalized to the [0, 1] range.

    :param data: bytes to read as an image.
    :type data: typing.BinaryIO
    :param normalize: scale the pixel components to the [0, 1] range.
    :type normalize: bool
    :return: list of pixels
    :rtype: list
    """
    width, height = _read_header(data)
    pixels = _read_pixels(data, width * height)
    if normalize:
        _normalize_pixels(pixels)
    return _group_pixels(pixels, width)
