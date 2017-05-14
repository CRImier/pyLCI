"""test for Checkbox"""
import unittest
from mock import patch, Mock
import logging
import os
import sys
os.sys.path.append(os.path.dirname(os.path.abspath('.')))

from checkbox import Checkbox

#set up logging
LOG_FORMAT = '%(levelname)s %(asctime)-15s %(name)s  %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


def get_mock_input():
    return Mock()

def get_mock_output(rows=2, cols=16):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols)
    return m

cb_name = "Test checkbox"

class TestCheckbox(unittest.TestCase):
    """tests dialog box class"""

    def test_constructor(self):
        """tests constructor"""
        checkbox = Checkbox([["Option", "option"]], get_mock_input(), get_mock_output(), name=cb_name)
        self.assertIsNotNone(checkbox)

    def test_keymap(self):
        """tests keymap"""
        checkbox = Checkbox([["Option", "option"]], get_mock_input(), get_mock_output(), name=cb_name)
        self.assertIsNotNone(checkbox.keymap)
        for key_name, callback in checkbox.keymap.iteritems():
            self.assertIsNotNone(callback)

    def test_left_key_returns_none(self):
        num_elements = 3
        contents = [["A"+str(i), "a"+str(i)] for i in range(num_elements)]
        cb = Checkbox(contents, get_mock_input(), get_mock_output(), name=cb_name)
        cb.refresh = lambda *args, **kwargs: None

        #Checking at the start of the list
        def scenario():
            cb.deactivate() #KEY_LEFT
            assert not cb.in_foreground
        with patch.object(cb, 'idle_loop', side_effect=scenario) as p:
            return_value = cb.activate()
        assert return_value is None
        
        #Checking at the end of the list
        def scenario():
            for i in range(num_elements):
                cb.move_down() #KEY_DOWN x3
            cb.deactivate() #KEY_LEFT
            assert not cb.in_foreground
        with patch.object(cb, 'idle_loop', side_effect=scenario) as p:
            return_value = cb.activate()
        assert return_value is None

    def test_enter_on_last_returns_right(self):
        num_elements = 3
        contents = [["A"+str(i), "a"+str(i)] for i in range(num_elements)]
        cb = Checkbox(contents, get_mock_input(), get_mock_output(), name=cb_name)
        cb.refresh = lambda *args, **kwargs: None

        #Checking at other elements - shouldn't return
        def scenario():
            cb.select_entry() #KEY_ENTER
            assert cb.in_foreground #Should still be active
            cb.deactivate() #because is not deactivated yet and would idle loop otherwise
        with patch.object(cb, 'idle_loop', side_effect=scenario) as p:
            return_value = cb.activate()
        assert return_value is None
        
        #Scrolling to the end of the list and pressing Enter - should return a correct dict
        def scenario():
            for i in range(num_elements):
                cb.move_down() #KEY_DOWN x3
            cb.select_entry() #KEY_ENTER
            assert not cb.in_foreground
        with patch.object(cb, 'idle_loop', side_effect=scenario) as p:
            return_value = cb.activate()
        assert isinstance(return_value, dict)
        assert all([isinstance(key, basestring) for key in return_value.keys()])
        assert all([isinstance(value, bool) for value in return_value.values()])


if __name__ == '__main__':
    unittest.main()
