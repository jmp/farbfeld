import io
import unittest
import farbfeld


class TestReadBytes(unittest.TestCase):
    def test_read_empty_data(self):
        self.assertRaises(
            farbfeld.InvalidFormat,
            farbfeld.read,
            io.BytesIO(b''),
        )

    def test_read_header_only(self):
        self.assertRaises(
            farbfeld.InvalidFormat,
            farbfeld.read,
            io.BytesIO(b'farbfeld'),
        )

    def test_read_wrong_header_no_data(self):
        self.assertRaises(
            farbfeld.InvalidFormat,
            farbfeld.read,
            io.BytesIO(b'dlefbraf'),
        )

    def test_read_correct_data_wrong_header(self):
        self.assertRaises(farbfeld.InvalidFormat, farbfeld.read, io.BytesIO(
            b'dlefbraf'  # magic
            b'\x00\x00\x00\x01'  # width
            b'\x00\x00\x00\x01'  # height
            b'\x01\x02\x03\x04\x05\x06\x07\x08'  # RGBA
        ))

    def test_read_valid_but_no_pixels(self):
        pixels = farbfeld.read(io.BytesIO(
            b'farbfeld'  # magic
            b'\x00\x00\x00\x00'  # width
            b'\x00\x00\x00\x00'  # height
        ))
        self.assertListEqual([], pixels)

    def test_read_valid_but_too_few_pixels(self):
        self.assertRaises(
            farbfeld.InvalidFormat,
            farbfeld.read,
            io.BytesIO(
                b'farbfeld'  # magic
                b'\x00\x00\x00\x01'  # width
                b'\x00\x00\x00\x02'  # height
                b'\xff\xff\xff\xff\xff\xff\xff\xff'  # RGBA
            ),
        )

    def test_read_valid_but_too_many_pixels(self):
        self.assertRaises(
            farbfeld.InvalidFormat,
            farbfeld.read,
            io.BytesIO(
                b'farbfeld'  # magic
                b'\x00\x00\x00\x01'  # width
                b'\x00\x00\x00\x01'  # height
                b'\xff\xff\xff\xff\xff\xff\xff\xff'  # RGBA
                b'\xff\xff\xff\xff\xff\xff\xff\xff'  # RGBA
            ),
        )

    def test_read_zero_width(self):
        pixels = farbfeld.read(io.BytesIO(
            b'farbfeld'  # magic
            b'\x00\x00\x00\x00'  # width
            b'\x00\x00\x00\x01'  # height
        ))
        self.assertListEqual([], pixels)

    def test_read_zero_height(self):
        pixels = farbfeld.read(io.BytesIO(
            b'farbfeld'  # magic
            b'\x00\x00\x00\x01'  # width
            b'\x00\x00\x00\x00'  # height
        ))
        self.assertListEqual([], pixels)

    def test_read_incomplete_pixel(self):
        self.assertRaises(
            farbfeld.InvalidFormat,
            farbfeld.read,
            io.BytesIO(
                b'farbfeld'  # magic
                b'\x00\x00\x00\x01'  # width
                b'\x00\x00\x00\x01'  # height
                b'\x00\x20\x00\x40\x00\x80\x00'  # RGBA
            ),
        )

    def test_read_single_pixel(self):
        pixels = farbfeld.read(io.BytesIO(
            b'farbfeld'  # magic
            b'\x00\x00\x00\x01'  # width
            b'\x00\x00\x00\x01'  # height
            b'\x00\x20\x00\x40\x00\x80\x00\xff'  # RGBA
        ))
        self.assertListEqual([[[32, 64, 128, 255]]], pixels)

    def test_read_two_by_two(self):
        pixels = farbfeld.read(io.BytesIO(
            b'farbfeld'  # magic
            b'\x00\x00\x00\x02'  # width
            b'\x00\x00\x00\x02'  # height
            b'\x00\x01\x00\x02\x00\x03\x00\x04'  # RGBA
            b'\x00\x05\x00\x06\x00\x07\x00\x08'  # RGBA
            b'\x00\x09\x00\x0a\x00\x0b\x00\x0c'  # RGBA
            b'\x00\x0d\x00\x0e\x00\x0f\x00\x10'  # RGBA
        ))
        self.assertListEqual([
            [[1, 2, 3, 4], [5, 6, 7, 8]],
            [[9, 10, 11, 12], [13, 14, 15, 16]]
        ], pixels)

    def test_read_normalize(self):
        pixels = farbfeld.read(io.BytesIO(
            b'farbfeld'  # magic
            b'\x00\x00\x00\x02'  # width
            b'\x00\x00\x00\x02'  # height
            b'\x00\x00\x00\x00\x00\x00\xff\xff'  # RGBA
            b'\xff\xff\xff\xff\xff\xff\xff\xff'  # RGBA
            b'\x33\x33\x33\x33\x33\x33\xff\xff'  # RGBA
            b'\x66\x66\x66\x66\x66\x66\xff\xff'  # RGBA
        ), normalize=True)
        self.assertListEqual([
            [[0.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 1.0]],
            [[0.2, 0.2, 0.2, 1.0], [0.4, 0.4, 0.4, 1.0]]
        ], pixels)
