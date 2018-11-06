"""test for loading indicators"""
import os
import unittest

from mock import patch, Mock

try:
    from ui.loading_indicators import BaseLoadingIndicator
except ImportError:
    print("Absolute imports failed, trying relative imports")
    os.sys.path.append(os.path.dirname(os.path.abspath(".")))
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
        from ui.loading_indicators import BaseLoadingIndicator


def get_mock_input():
    return Mock()


def get_mock_output(rows=8, cols=21):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols, type=["char"])
    return m


class TestBaseLoadingIndicator(unittest.TestCase):

    @patch("ui.loading_indicators.BaseLoadingIndicator.pause")
    @patch("ui.loading_indicators.BaseLoadingIndicator.resume")
    def test_with_loading_indicator_paused_construct(self, resume, pause):
        i = get_mock_input()
        o = get_mock_output()
        li = BaseLoadingIndicator(i, o)
        self.assertFalse(pause.called)
        self.assertFalse(resume.called)
        with li.paused:
            self.assertTrue(pause.called)
            self.assertFalse(resume.called)
        self.assertTrue(resume.called)


if __name__ == "__main__":
    unittest.main()
