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
    :type data: io.RawIOBase
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


def _normalize(rgba):
    """
    Scales the components of the given RGBA values to the range [0, 1].

    :param rgba: components to scale.
    :type rgba: tuple of int
    :return: normalized components.
    :rtype: list of int
    """
    return [value / COMPONENT_MAX for value in rgba]


def _read_pixels(buffer, width, height, normalize=False):
    """
    Unpacks pixels from the given buffer.

    :param buffer: raw pixel data to read from.
    :type buffer: io.RawIOBase
    :param width: image width
    :type width: int
    :param height: image height
    :type height: int
    :param normalize: scale pixel components to the [0, 1] range
    :return: pixel data as a nested list.
    :rtype: list
    """
    rows = []
    column = []
    num_pixels = 0
    max_pixels = width * height
    for rgba in PIXEL_STRUCT.iter_unpack(buffer.read()):
        if normalize:
            column.append(_normalize(rgba))
        else:
            column.append(list(rgba))
        if len(column) >= width:
            rows.append(column)
            column = []
        num_pixels += 1
    if num_pixels != max_pixels:
        raise InvalidFormat("number of pixels does not match header")
    return rows


def read(data, normalize=False):
    """
    Reads the given raw image data (for example the contents of a file)
    and returns the corresponding pixels as a list. The list contains
    another list for each row of the image, and each nested list contains
    the pixels on that row as a list [r, g, b, a].

    :param data: bytes to read as an image.
    :type data: io.RawIOBase
    :param normalize: scale the pixel components to the [0, 1] range.
    :type normalize: bool
    :return: list of pixels
    :rtype: list
    """
    width, height = _read_header(data)
    pixels = _read_pixels(data, width, height, normalize)
    return pixels
