import unittest

from mock import patch, Mock

from ui.loading_indicators import BaseLoadingIndicator


def get_mock_input():
    return Mock()


def get_mock_output(rows=8, cols=21):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols, type=["char"])
    return m


class TestBaseLoadingIndicator(unittest.TestCase):

    @patch("ui.refresher.Refresher.pause")
    @patch("ui.refresher.Refresher.resume")
    def test_with_paused(self, resume, pause):
        i = get_mock_input()
        o = get_mock_output()
        li = BaseLoadingIndicator(i, o)
        self.assertFalse(pause.called)
        self.assertFalse(resume.called)
        with li.paused():
            self.assertTrue(pause.called)
            self.assertFalse(resume.called)
        self.assertTrue(resume.called)
