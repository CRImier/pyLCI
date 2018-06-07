"""test for UniversalInput"""
import os
import unittest

from mock import patch, Mock

try:
    from ui import UniversalInput, CharArrowKeysInput, NumpadCharInput, NumpadNumberInput, NumpadHexInput
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
        from input import UniversalInput
        from char_input import CharArrowKeysInput
        from numpad_input import NumpadCharInput, NumpadNumberInput, NumpadHexInput

zerophone_keys = [ "KEY_LEFT", "KEY_UP", "KEY_DOWN", "KEY_RIGHT", "KEY_ENTER",
                   "KEY_1", "KEY_2", "KEY_3", "KEY_4", "KEY_5", "KEY_6", "KEY_7",
                   "KEY_8", "KEY_9", "KEY_*", "KEY_0", "KEY_#", "KEY_F1", "KEY_F2",
                   "KEY_ANSWER", "KEY_HANGUP", "KEY_PAGEUP", "KEY_PAGEDOWN", "KEY_F5", 
                   "KEY_F6", "KEY_VOLUMEUP", "KEY_VOLUMEDOWN", "KEY_PROG1", "KEY_PROG2",
                   "KEY_CAMERA"]
hardpass_keys = [ "KEY_1", "KEY_UP", "KEY_3", "KEY_LEFT", "KEY_ENTER", "KEY_RIGHT", "KEY_7",
                  "KEY_DOWN", "KEY_9", "KEY_*", "KEY_0", "KEY_#"]
ad_oledbon_keys = [ "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT", "KEY_ENTER", "KEY_PAGEUP",
                    "KEY_PAGEDOWN", "KEY_PROG1"]

type_map = {"zerophone":zerophone_keys, "hardpass":hardpass_keys, "adafruit_oledbonnet":ad_oledbon_keys}

def get_mock_input(type):
    assert(type in type_map.keys())
    m = Mock()
    m.configure_mock(available_keys = {"mock_driver": type_map[type]})
    return m

def get_mock_output(rows=8, cols=21):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols, type=["char"])
    return m

ui_name = "Test UniversalInput"


class TestUniversalInput(unittest.TestCase):
    """test UniversalInput class"""

    def test_zerophone(self):
        """tests whether UniversalInput works on ZeroPhone"""
        ui = UniversalInput(get_mock_input("zerophone"), get_mock_output(), name=ui_name)
        self.assertIsInstance(ui, NumpadCharInput)

    def test_hardpass(self):
        """tests whether UniversalInput works on Hardpass"""
        ui = UniversalInput(get_mock_input("hardpass"), get_mock_output(), name=ui_name)
        self.assertIsInstance(ui, CharArrowKeysInput)

    def test_adafruit_oled_bonnet(self):
        """tests whether UniversalInput works on Adafruit OLED Bonnet"""
        ui = UniversalInput(get_mock_input("adafruit_oledbonnet"), get_mock_output(), name=ui_name)
        self.assertIsInstance(ui, CharArrowKeysInput)


if __name__ == '__main__':
    unittest.main()
