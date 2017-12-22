"""test for Checkbox"""
import unittest
from mock import patch, Mock
import logging
import os
import sys

from helpers.logger import setup_logger
from ui.config_manager import UIConfigManager

os.sys.path.append(os.path.dirname(os.path.abspath('.')))

#set up logging
LOG_FORMAT = '%(levelname)s %(asctime)-15s %(name)s  %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

logger = setup_logger(__name__, logging.WARNING)


class TestUIConfigManager(unittest.TestCase):
    """tests config manager class"""

    def test_update_config(self):
        cm = UIConfigManager()
        config_a = {"a":{"this1":"is original"}, "b":{"value":"to_be_replaced"}, 
                       "c":"old_element_value", "e":{"this":"remains"}}
        config_b = {"a":{"this2":"is_new"}, "b":{"value":"was_replaced"}, 
                       "c":"new_element_value", "d":{"this":"is_new"}}
        new_config = cm.update_config(config_a, config_b)
        self.assertEquals(new_config, {'a': {'this1': 'is original', 'this2': 'is_new'}, 
                                  'c': 'new_element_value', 'b': {'value': 'was_replaced'},
                                  'e': {'this': 'remains'}, 'd': {'this': 'is_new'}})


if __name__ == '__main__':
    unittest.main()
