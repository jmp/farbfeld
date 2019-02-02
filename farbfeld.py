"""
Module for working with the farbfile image format.

This module can be used to reading or writing pixel data from/to farbfeld
image files. For reading and writing, use the functions 'read' and 'write',
respectively.

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
values are between 0 and 65535. For visualizing the image, you may
want to scale the values to the [0, 1] or [0, 255] range.

To write a farbfeld image:

>>> with open('image.ff', 'wb') as f:
...     write(f, data)

The data should be given in the same format as returned by the 'read'
function (i.e. a nested list). If the format is not correct, an
exception will be raised.
"""


__all__ = ['read', 'write']


import functools
import itertools
import numbers
import struct


# The file begins with eight magic bytes
HEADER_MAGIC = b'farbfeld'

# Following the magic bytes are width and
# height as 32-bit unsigned big-endian integers.
HEADER_STRUCT = struct.Struct('>8s2L')

# After that are pixel components (RGBA),
# each being 16-bit unsigned big-endian integers.
PIXEL_STRUCT = struct.Struct('>4H')

# A pixel consists of 4 components, each being
# an 16-bit unsigned integer between 0 and 65535.
COMPONENT_NUM = 4
COMPONENT_MIN = 0
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


def read(data):
    """
    Reads the given raw image data (for example the contents of a file)
    and returns the corresponding pixels as a list. The list contains
    another list for each row of the image, and each nested list contains
    the pixels on that row as a list [r, g, b, a].

    :param data: bytes to read as an image.
    :type data: typing.BinaryIO
    :return: list of pixels
    :rtype: list
    """
    width, height = _read_header(data)
    pixels = _read_pixels(data, width * height)
    return _group_pixels(pixels, width)


def _calculate_dimensions(data):
    """
    Returns the with and height of the given pixel data.

    The height of the image is the number of rows in the list,
    while the width of the image is determined by the number of
    pixels on the first row. It is assumed that each row contains
    the same number of pixels.

    :param data: pixel data
    :type data: list
    :return: width and height as a tuple
    :rtype: tuple
    """
    try:
        width = 0
        height = len(data)
        if height != 0:
            width = len(data[0])
        return width, height
    except (IndexError, TypeError):
        # Either data is not subscribable, or the
        # length of the first row cannot be obtained.
        raise ValueError("invalid pixel data - could not determine dimensions")


def _validate_component(value):
    """
    Make sure that the value is an integer within the
    range [COMPONENT_MIN, COMPONENT_MAX]. If not, then
    a ValueError is raised.

    :param value: value to check
    :type value: int
    :raises ValueError
    """
    if not isinstance(value, numbers.Integral):
        raise ValueError("components must be integers")
    if value < COMPONENT_MIN or value > COMPONENT_MAX:
        raise ValueError(
            "component value must be between "
            f"{COMPONENT_MIN} and {COMPONENT_MAX}"
        )


def _validate_items(length, item_validator, items):
    """
    Make sure there are exactly 'length' items, each valid according to the
    given validator. If any validation fails, ValueError is raised.

    :param length: expected number of items
    :type length: int
    :param item_validator: function that validates each item
    :type item_validator: typing.Callable
    :param items: list of items to check
    :type items: list
    :raises ValueError
    """
    if len(items) != length:
        raise ValueError("unexpected length")
    for item in items:
        item_validator(item)


def _validate_data(data, width, height):
    """
    Make sure the given pixel data is valid:

     * It must have exactly 'height' rows.
     * Each row must have exactly 'width' pixels.
     * Each pixel must have exactly COMPONENT_NUM components.
     * Each component must be a valid 8-bit unsigned integer.

    :param data: pixel data to validate
    :type data: list
    :param width: number of pixels per row
    :type width: int
    :param height: number of rows
    :type height: int
    """
    validate_pixel = functools.partial(
        _validate_items,
        COMPONENT_NUM,
        _validate_component,
    )
    validate_row = functools.partial(
        _validate_items,
        width,
        validate_pixel,
    )
    validate_all = functools.partial(
        _validate_items,
        height,
        validate_row,
    )
    validate_all(data)


def _write_header(file, width, height):
    """
    Write the farbfeld header to the given file.
    The header contains the magic string 'farbfeld' followed by
    the width and height of the image.

    :param file: file to write to
    :type file: typing.BinaryIO
    :param width: image width in pixels
    :type width: int
    :param height: image height in pixels
    :type height: int
    """
    file.write(HEADER_STRUCT.pack(HEADER_MAGIC, width, height))


def _write_pixels(file, data):
    """
    Write pixel data to the given file.

    :param file: file to write to
    :type file: typing.BinaryIO
    :param data: pixels to write
    :type data: list
    """
    for pixel in itertools.chain.from_iterable(data):
        file.write(PIXEL_STRUCT.pack(*pixel))


def write(file, data):
    """
    Write the image header and given pixel data to the given file.

    Before writing, the dimensions of the image are calculated
    based on the given data. The data is then validated to make
    sure it contains the consistent number of pixels for each
    row, the correct number of components for each pixel,
    and valid values for each component.

    :param file: file to write to
    :type file: typing.BinaryIO
    :param data: pixels to write
    :type data: list
    """
    width, height = _calculate_dimensions(data)
    _validate_data(data, width, height)
    _write_header(file, width, height)
    _write_pixels(file, data)
