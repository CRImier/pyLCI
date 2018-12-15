"""test for Printer functions"""
import os
import unittest

from mock import patch, Mock

try:
    from ui import Printer, GraphicsPrinter
except ImportError:
    print("Absolute imports failed, trying relative imports")
    os.sys.path.append(os.path.dirname(os.path.abspath('.')))
    # Store original __import__
    orig_import = __import__

    def import_mock(name, *args, **kwargs):
        if name in ['helpers']:
            return Mock()
        elif name == 'ui.utils':
            import utils
            return utils
        return orig_import(name, *args, **kwargs)

    with patch('__builtin__.__import__', side_effect=import_mock):
        from printer import Printer, GraphicsPrinter

def get_mock_input():
    return Mock()

def get_mock_output(rows=8, cols=21):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols, type=["char"])
    return m

def get_mock_graphical_output(width, height, mode="1", cw=6, ch=8):
    m = get_mock_output(rows=width/cw, cols=height/ch)
    m.configure_mock(width=width, height=height, device_mode=mode, char_height=ch, char_width=cw, type=["b&w-pixel"])
    return m

class TestPrinter(unittest.TestCase):
    """tests Printer functions"""

    def test_runs_with_none_i(self):
        """tests constructor"""
        assert Printer("test", None, get_mock_output(), 0) == None

    @unittest.skip("Need to feed it an image or something")
    def test_graphical_printer(self):
        GraphicsPrinter("test", None, get_mock_output(128, 64), 0)
        assert o.display_image.called
	GraphicsPrinter("test", None, get_mock_output(128, 128), 0)
        assert o.display_image.called
	GraphicsPrinter("test", None, get_mock_output(128, 32), 0)
        assert o.display_image.called
	GraphicsPrinter("test", None, get_mock_output(56, 75), 0)
        assert o.display_image.called
        assert o.display_image.call_count == 1

    def test_shows_data_on_screen(self):
        """Tests whether the Printer outputs data on screen when it's ran"""
        i = get_mock_input()
        o = get_mock_output()

        Printer("test", i, o, 0)

        assert o.display_data.called
        assert o.display_data.call_count == 1
        assert o.display_data.call_args[0] == ('test',)

if __name__ == '__main__':
    unittest.main()
