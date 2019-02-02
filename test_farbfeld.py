import io
import unittest
import farbfeld


class ReadTest(unittest.TestCase):
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
            [[9, 10, 11, 12], [13, 14, 15, 16]],
        ], pixels)


class WriteTest(unittest.TestCase):
    def test_write_invalid_data(self):
        self.assertRaises(ValueError, farbfeld.write, io.BytesIO(), None)

    def test_write_zero_height(self):
        file = io.BytesIO()
        farbfeld.write(file, [])
        file.seek(0)
        self.assertEqual(
            file.read(),
            b'farbfeld'  # magic
            b'\x00\x00\x00\x00'  # width
            b'\x00\x00\x00\x00'  # height
        )

    def test_write_zero_width(self):
        file = io.BytesIO()
        farbfeld.write(file, [[]])
        file.seek(0)
        self.assertEqual(
            file.read(),
            b'farbfeld'  # magic
            b'\x00\x00\x00\x00'  # width
            b'\x00\x00\x00\x01'  # height
        )

    def test_write_incomplete_pixels(self):
        self.assertRaises(ValueError, farbfeld.write, io.BytesIO(), [[[]]])

    def test_write_too_few_components(self):
        self.assertRaises(
            ValueError,
            farbfeld.write,
            io.BytesIO(),
            [[[1, 2, 3]]],
        )

    def test_write_too_many_components(self):
        self.assertRaises(
            ValueError,
            farbfeld.write,
            io.BytesIO(),
            [[[1, 2, 3, 4, 5]]],
        )

    def test_write_component_out_of_range(self):
        self.assertRaises(
            ValueError,
            farbfeld.write,
            io.BytesIO(),
            [[[0, 0, 0, -1]]],
        )
        self.assertRaises(
            ValueError,
            farbfeld.write,
            io.BytesIO(),
            [[[0, 0, 0, 65536]]],
        )

    def test_write_invalid_component(self):
        self.assertRaises(
            ValueError,
            farbfeld.write,
            io.BytesIO(),
            [[[0, 0, 0, 0.5]]],
        )
        self.assertRaises(
            ValueError,
            farbfeld.write,
            io.BytesIO(),
            [[[0, 0, 0, '1']]],
        )
        self.assertRaises(
            ValueError,
            farbfeld.write,
            io.BytesIO(),
            [[[0, 0, 0, None]]],
        )

    def test_write_inconsistent_width(self):
        self.assertRaises(ValueError, farbfeld.write, io.BytesIO(), [[
            [0, 0, 0, 0], [0, 0, 0, 0],  # first row, two pixels
        ], [
            [0, 0, 0, 0],  # second row, only one pixel
        ]])

    def test_write_single_pixel(self):
        file = io.BytesIO()
        farbfeld.write(file, [[[32, 64, 128, 255]]])
        file.seek(0)
        self.assertEqual(
            file.read(),
            b'farbfeld'  # magic
            b'\x00\x00\x00\x01'  # width
            b'\x00\x00\x00\x01'  # height
            b'\x00\x20\x00\x40\x00\x80\x00\xff'  # RGBA
        )

    def test_write_two_by_two(self):
        file = io.BytesIO()
        farbfeld.write(file, [
            [[1, 2, 3, 4], [5, 6, 7, 8]],
            [[9, 10, 11, 12], [13, 14, 15, 16]],
        ])
        file.seek(0)
        self.assertEqual(
            file.read(),
            b'farbfeld'  # magic
            b'\x00\x00\x00\x02'  # width
            b'\x00\x00\x00\x02'  # height
            b'\x00\x01\x00\x02\x00\x03\x00\x04'  # RGBA
            b'\x00\x05\x00\x06\x00\x07\x00\x08'  # RGBA
            b'\x00\x09\x00\x0a\x00\x0b\x00\x0c'  # RGBA
            b'\x00\x0d\x00\x0e\x00\x0f\x00\x10'  # RGBA
        )
