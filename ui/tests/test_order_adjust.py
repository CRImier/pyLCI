"""test for OrderAdjust"""
import os
import unittest

from mock import patch, Mock

try:
    from ui import OrderAdjust
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
        from order_adjust import OrderAdjust

def get_mock_input():
    return Mock()


def get_mock_output(rows=8, cols=21):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols, type=["char"])
    return m

shorthands = {
    "u":"KEY_UP",
    "d":"KEY_DOWN",
    "l":"KEY_LEFT",
    "e":"KEY_ENTER"}

def execute_shorthand(oa, shorthand):
    # A helper function for us to easier test behaviour of OrderAdjust
    shorthand_key = shorthands[shorthand]
    oa.keymap[shorthand_key]()

oa_name = "Test OrderAdjust"


class TestOrderAdjust(unittest.TestCase):
    """test OrderAdjust class"""

    def test_constructor(self):
        """tests constructor"""
        oa = OrderAdjust(["1", "2", "3"], get_mock_input(), get_mock_output(), name=oa_name, config={})
        self.assertIsNotNone(oa)

    def test_left_returns_none(self):
        oa = OrderAdjust(["1", "2", "3"], get_mock_input(), get_mock_output(), name=oa_name, config={})
        oa.refresh = lambda *args, **kwargs: None #not needed

        # Checking without changing value
        def scenario():
            execute_shorthand(oa, 'l')
            assert not oa.is_active

        with patch.object(oa, 'idle_loop', side_effect=scenario) as p:
            return_value = oa.activate()
        assert return_value is None

        # Checking after entering some keys
        test_keys = "d"*5+"u"*3
        def scenario():
            for key in test_keys:
                execute_shorthand(oa, key)
            execute_shorthand(oa, 'l')
            assert not oa.is_active

        with patch.object(oa, 'idle_loop', side_effect=scenario) as p:
            return_value = oa.activate()
        assert return_value is None

    def test_entering_value(self):
        start = ["1", "3", "2"]
        oa = OrderAdjust(start, get_mock_input(), get_mock_output(), name=oa_name, config={})
        oa.refresh = lambda *args, **kwargs: None

        expected_output = ["1", "2", "3"]

        # down, enter (pick 3), down, enter (put 3), down, enter (accept)
        test_keys = "dedede"
        def scenario():
            for key in test_keys:
                execute_shorthand(oa, key)
            assert not oa.is_active

        with patch.object(oa, 'idle_loop', side_effect=scenario) as p:
            return_value = oa.activate()
        assert return_value == expected_output

        oa = OrderAdjust(start, get_mock_input(), get_mock_output(), name=oa_name, config={})
        # down, down, enter (pick 2), up, enter (put 2), down, down, enter (accept)
        test_keys = "ddeuedde"
        def scenario():
            for key in test_keys:
                execute_shorthand(oa, key)
            assert not oa.is_active

        with patch.object(oa, 'idle_loop', side_effect=scenario) as p:
            return_value = oa.activate()
        assert return_value == expected_output

    def test_shows_data_on_screen(self):
        """Tests whether the OrderAdjust outputs data on screen when it's ran"""
        i = get_mock_input()
        o = get_mock_output()
        start = [str(x) for x in range(o.rows+4)]
        oa = OrderAdjust(start, i, o, name=oa_name, config={})

        def scenario():
            assert o.display_data.called
            assert o.display_data.call_args[0] == tuple([str(x) for x in range(o.rows)])
            for i in range(o.rows+1):
                execute_shorthand(oa, "d")
            assert o.display_data.call_args[0] == tuple([str(x) for x in range(2, o.rows+2)])
            for i in range(3):
                execute_shorthand(oa, "d")
            execute_shorthand(oa, "e")
            assert not oa.is_active  # Should exit on last "e"

        with patch.object(oa, 'idle_loop', side_effect=scenario) as p:
            oa.activate()
            #The scenario should only be called once
            assert oa.idle_loop.called
            assert oa.idle_loop.call_count == 1

        # moved o.rows+4, and one more refresh on activate()
        assert o.display_data.call_count == o.rows+4+1

if __name__ == '__main__':
    unittest.main()
