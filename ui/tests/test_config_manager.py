"""test for Checkbox"""
import os
import unittest


try:
    from ui.config_manager import UIConfigManager
except ImportError:
    print("Absolute imports failed, trying relative imports")
    os.sys.path.append(os.path.dirname(os.path.abspath('.')))
    from config_manager import UIConfigManager


class TestUIConfigManager(unittest.TestCase):
    """tests config manager class"""

    def test_update_config(self):
        cm = UIConfigManager()
        config_a = {
            "a": {"this1": "is original"},
            "b": {"value": "to_be_replaced"},
            "c": "old_element_value",
            "e": {"this": "remains"}
        }
        config_b = {
            "a": {"this2": "is_new"},
            "b": {"value": "was_replaced"},
            "c": "new_element_value",
            "d": {"this": "is_new"}
        }
        new_config = cm.update_config(config_a, config_b)
        self.assertEquals(new_config, {
            'a': {'this1': 'is original', 'this2': 'is_new'},
            'b': {'value': 'was_replaced'},
            'c': 'new_element_value',
            'd': {'this': 'is_new'},
            'e': {'this': 'remains'}
        })


if __name__ == '__main__':
    unittest.main()
