# -*- coding: utf-8 -*-
"""tests for ui.funcs"""
import os
import unittest

from mock import patch, Mock
from PIL import Image, ImageFont, ImageChops

try:
    from ui import ellipsize, format_for_screen as ffs, replace_filter_ascii as rfa, add_character_replacement
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
        from funcs import ellipsize, format_for_screen as ffs, replace_filter_ascii as rfa, add_character_replacement


c_name = "Test funcs"


class TestFuncs(unittest.TestCase):
    """Tests the UI helper functions"""

    def test_rfa(self):
        """Tests replace_filter_ascii, as well as add_character_replacement"""
        assert(rfa(u"may I have some lööps bröther") == "may I have some loops brother")
        # sneaky Russian letters
        assert(rfa(u"may I have some lооps brоther") == "may I have some loops brother")
        assert(rfa(u"may I have some lооps бrоther") == "may I have some loops brother")
        # Testing non-Unicode strings
        assert(rfa('\xc3\x85land Islands') == "Aland Islands")
        # And the corresponding Unicode string, just in case
        assert(rfa(u"Åland Islands") == "Aland Islands")

    def test_ffs(self):
        """Tests format_for_screen"""
        assert(ffs("Hello", 16) == ["Hello "])
        assert(ffs("may I have some loops brother", 16) == ['may I have some ', 'loops brother '])

    def test_ellipsize(self):
        """Tests ellipsize"""
        text = "ooooooo"
        assert (ellipsize(text, 5) == "oo...")
        assert (ellipsize(text, 16) == text)

if __name__ == '__main__':
    unittest.main()
