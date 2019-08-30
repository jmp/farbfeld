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


from functools import partial
from itertools import chain
from numbers import Integral
from struct import error, Struct
from typing import BinaryIO, Tuple, List, Callable, TypeVar

# The file begins with eight magic bytes
HEADER_MAGIC: bytes = b'farbfeld'

# Following the magic bytes are width and
# height as 32-bit unsigned big-endian integers.
HEADER_STRUCT: Struct = Struct('>8s2L')

# After that are pixel components (RGBA),
# each being 16-bit unsigned big-endian integers.
PIXEL_STRUCT: Struct = Struct('>4H')

# A pixel consists of 4 components, each being
# an 16-bit unsigned integer between 0 and 65535.
COMPONENT_NUM: int = 4
COMPONENT_MIN: int = 0
COMPONENT_MAX: int = 2**16 - 1

# Type aliases
T = TypeVar('T')  # pylint: disable=invalid-name
Pixel = List[int]
Image = List[List[Pixel]]
Validator = Callable[[T], None]


class InvalidFormat(Exception):
    """
    Raised if the file header is invalid, or the file
    is otherwise formatted in an invalid way.
    """


def _read_header(data: BinaryIO) -> Tuple[int, int]:
    """
    Extracts the header part from the given data, validates it,
    and returns the image width and height based on it.

    :param data: image data.
    :return: tuple containing the image width and height.
    """
    # Unpack header
    try:
        header = data.read(HEADER_STRUCT.size)
        magic, width, height = HEADER_STRUCT.unpack(header)
    except error:
        raise InvalidFormat('invalid header format')

    # Make sure it's a farbfeld file
    if magic != HEADER_MAGIC:
        raise InvalidFormat('invalid header signature')

    return width, height


def _read_pixels(buffer: BinaryIO, count: int) -> List[Pixel]:
    """
    Unpacks pixels from the given buffer.

    :param buffer: raw pixel data to read from.
    :param count: number of pixels to read
    :return: pixel data as a nested list.
    """
    pixels = []
    try:
        # Unpack the buffer pixel by pixel
        for rgba in PIXEL_STRUCT.iter_unpack(buffer.read()):
            pixels.append(list(rgba))
    except error:
        # Some components are missing
        raise InvalidFormat("incomplete pixels")

    # Make sure we got the correct amount of pixels
    if len(pixels) != count:
        raise InvalidFormat("number of pixels does not match header")

    return pixels


def _group_pixels(pixels: List[Pixel], num_rows: int) -> Image:
    """
    Group the given pixels into a nested list containing rows of pixels.

    :param pixels:
    :return: pixels grouped by row
    """
    offset = 0
    rows = []
    while offset < len(pixels):
        rows.append(pixels[offset:offset + num_rows])
        offset += num_rows
    return rows


def read(data: BinaryIO) -> Image:
    """
    Reads the given raw image data (for example the contents of a file)
    and returns the corresponding pixels as a list. The list contains
    another list for each row of the image, and each nested list contains
    the pixels on that row as a list [r, g, b, a].

    :param data: bytes to read as an image.
    :return: list of pixels
    """
    width, height = _read_header(data)
    pixels = _read_pixels(data, width * height)
    return _group_pixels(pixels, width)


def _calculate_dimensions(image: Image) -> Tuple[int, int]:
    """
    Returns the width and height of the given pixel data.

    The height of the image is the number of rows in the list,
    while the width of the image is determined by the number of
    pixels on the first row. It is assumed that each row contains
    the same number of pixels.

    :param image: pixel data
    :return: width and height as a tuple
    """
    try:
        width = 0
        height = len(image)
        if height != 0:
            width = len(image[0])
        return width, height
    except (IndexError, TypeError):
        # Either data is not subscribable, or the
        # length of the first row cannot be obtained.
        raise ValueError("invalid pixel data - could not determine dimensions")


def _validate_component(value: int) -> None:
    """
    Make sure that the value is an integer within the
    range [COMPONENT_MIN, COMPONENT_MAX]. If not, then
    a ValueError is raised.

    :param value: value to check
    :raises ValueError
    """
    if not isinstance(value, Integral):
        raise ValueError("components must be integers")
    if not COMPONENT_MIN <= value <= COMPONENT_MAX:
        raise ValueError(
            "component value must be between "
            f"{COMPONENT_MIN} and {COMPONENT_MAX}"
        )


def _validate(length: int, validator: Validator, items: List[T]) -> None:
    """
    Make sure there are exactly 'length' items, each valid according to the
    given validator. If any validation fails, ValueError is raised.

    :param length: expected number of items
    :param validator: function that validates each item
    :param items: list of items to check
    :raises ValueError
    """
    if len(items) != length:
        raise ValueError("unexpected length")
    for item in items:
        validator(item)


def _validate_data(image: Image, width: int, height: int) -> None:
    """
    Make sure the given pixel data is valid:

     * It must have exactly 'height' rows.
     * Each row must have exactly 'width' pixels.
     * Each pixel must have exactly COMPONENT_NUM components.
     * Each component must be a valid 8-bit unsigned integer.

    :param image: pixel data to validate
    :param width: number of pixels per row
    :param height: number of rows
    """
    validate_pixel = partial(
        _validate,
        COMPONENT_NUM,
        _validate_component,
    )
    validate_row = partial(
        _validate,
        width,
        validate_pixel,
    )
    validate_all = partial(
        _validate,
        height,
        validate_row,
    )
    validate_all(image)


def _write_header(file: BinaryIO, width: int, height: int) -> None:
    """
    Write the farbfeld header to the given file.
    The header contains the magic string 'farbfeld' followed by
    the width and height of the image.

    :param file: file to write to
    :param width: image width in pixels
    :param height: image height in pixels
    """
    file.write(HEADER_STRUCT.pack(HEADER_MAGIC, width, height))


def _write_pixels(file: BinaryIO, image: Image) -> None:
    """
    Write pixel data to the given file.

    :param file: file to write to
    :param image: pixels to write
    """
    for pixel in chain.from_iterable(image):
        file.write(PIXEL_STRUCT.pack(*pixel))


def write(file: BinaryIO, image: Image) -> None:
    """
    Write the image header and given pixel data to the given file.

    Before writing, the dimensions of the image are calculated
    based on the given data. The data is then validated to make
    sure it contains the consistent number of pixels for each
    row, the correct number of components for each pixel,
    and valid values for each component.

    :param file: file to write to
    :param image: pixels to write
    """
    width, height = _calculate_dimensions(image)
    _validate_data(image, width, height)
    _write_header(file, width, height)
    _write_pixels(file, image)
