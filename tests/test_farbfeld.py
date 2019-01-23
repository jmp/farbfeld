import unittest
import farbfeld


class TestReadBytes(unittest.TestCase):
    def test_read_empty_data(self):
        self.assertRaises(farbfeld.InvalidFormat, farbfeld.read, b'')

    def test_read_header_only(self):
        self.assertRaises(farbfeld.InvalidFormat, farbfeld.read, b'farbfeld')

    def test_read_valid_but_no_pixels(self):
        pixels = farbfeld.read((
            b'farbfeld'  # magic
            b'\x00\x00\x00\x00'  # width
            b'\x00\x00\x00\x00'  # height
        ))
        self.assertListEqual([], pixels)

    def test_read_zero_width(self):
        pixels = farbfeld.read((
            b'farbfeld'  # magic
            b'\x00\x00\x00\x00'  # width
            b'\x00\x00\x00\x01'  # height
        ))
        self.assertListEqual([], pixels)

    def test_read_zero_height(self):
        pixels = farbfeld.read((
            b'farbfeld'  # magic
            b'\x00\x00\x00\x01'  # width
            b'\x00\x00\x00\x00'  # height
        ))
        self.assertListEqual([], pixels)

    def test_read_single_pixel(self):
        pixels = farbfeld.read((
            b'farbfeld'  # magic
            b'\x00\x00\x00\x01'  # width
            b'\x00\x00\x00\x01'  # height
            b'\x00\x20\x00\x40\x00\x80\x00\xff'  # RGBA
        ))
        self.assertListEqual([[[32, 64, 128, 255]]], pixels)

    def test_read_two_by_two(self):
        pixels = farbfeld.read((
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
