"""tests for Canvas"""
import os
import unittest

from mock import patch, Mock
from PIL import Image

try:
    from ui import Canvas
except ImportError:
    print("Absolute imports failed, trying relative imports")
    os.sys.path.append(os.path.dirname(os.path.abspath('.')))
    # Store original __import__
    orig_import = __import__

    def import_mock(name, *args):
        if name in ['helpers']:
            return Mock()
        elif name == 'ui.utils':
            import utils
            return utils
        return orig_import(name, *args)

    with patch('__builtin__.__import__', side_effect=import_mock):
        from canvas import Canvas


def get_mock_output(width=128, height=64, mode="1"):
    m = Mock()
    m.configure_mock(width=width, height=height, device_mode=mode, type=["b&w-pixel"])
    return m


c_name = "Test Canvas"


class TestCanvas(unittest.TestCase):
    """Tests the Canvas class"""

    def test_constructor(self):
        """Tests constructor"""
        c = Canvas(get_mock_output(), name=c_name)
        self.assertIsNotNone(c)

    def test_base_image(self):
        """Tests whether the base_image kwarg works"""
        w = 128
        h = 64
        i = Image.new("1", (w, h) )
        c = Canvas(get_mock_output(), base_image=i, name=c_name)
        assert(c.image == i)
        assert(c.size == (w, h))

    def test_coords_filtering(self):
        """tests whether the coordinate filtering works"""
        w = 128
        h = 64
        c = Canvas(get_mock_output(width=w, height=h), name=c_name)
        assert (c.check_coordinates((0, 1)) == (0, 1))
        assert (c.check_coordinates(("-2", "-3")) == (w-2, h-3))
        assert (c.check_coordinates((0, 1, 2, 3)) == (0, 1, 2, 3))
        assert (c.check_coordinates((0, 1, "-2", "-3")) == (0, 1, w-2, h-3))
        assert (c.check_coordinates(("-0", "-1", "-2", "-3")) == (w, h-1, w-2, h-3))
        assert (c.check_coordinates(("-0", "1", "-2", "-3")) == (w, h+1, w-2, h-3))


if __name__ == '__main__':
    unittest.main()
