"""test for CharArrowKeysInput"""
import os
import unittest

from mock import patch, Mock

try:
    from ui import CharArrowKeysInput
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
        from char_input import CharArrowKeysInput

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
    "r":"KEY_RIGHT",
    "e":"KEY_ENTER"}

def execute_shorthand(ci, shorthand):
    # A helper function for us to easier test behaviour of CharArrowKeysInput
    shorthand_key = shorthands[shorthand]
    ci.keymap[shorthand_key]()

ci_name = "Test CharArrowKeysInput"


class TestCharArrowKeysInput(unittest.TestCase):
    """test CharArrowKeysInput class"""

    def test_constructor(self):
        """tests constructor"""
        ci = CharArrowKeysInput(get_mock_input(), get_mock_output(), name=ci_name)
        self.assertIsNotNone(ci)

    def test_initial_value_support(self):
        """tests support for the obsolete attribute"""
        value = "ololo"
        ci = CharArrowKeysInput(get_mock_input(), get_mock_output(), initial_value = value, name=ci_name)
        assert ci.value == list(value)

    def test_value_leakage(self):
        """tests whether the action key settings of one CharArrowKeysInput leaks into another"""
        i = get_mock_input()
        o = get_mock_output()
        c1 = CharArrowKeysInput(i, o, value="1", name=ci_name + "1")
        c2 = CharArrowKeysInput(i, o, value="2", name=ci_name + "2")
        c3 = CharArrowKeysInput(i, o, name=ci_name + "3")
        assert (c1.value != c2.value)
        assert (c2.value != c3.value)
        assert (c1.value != c3.value)

    def test_f1_left_returns_none(self):
        ci = CharArrowKeysInput(get_mock_input(), get_mock_output(), name=ci_name)
        ci.refresh = lambda *args, **kwargs: None #not needed

        # Checking at the start of the list
        def scenario():
            ci.keymap["KEY_LEFT"]()
            assert not ci.in_foreground

        with patch.object(ci, 'idle_loop', side_effect=scenario) as p:
            return_value = ci.activate()
        assert return_value is None

        # Checking after entering some keys
        letters_entered = 5
        test_keys = "ur"*letters_entered
        def scenario():
            for key in test_keys:
                execute_shorthand(ci, key)
            for i in range(letters_entered):
                execute_shorthand(ci, 'l')
                assert ci.in_foreground #Not yet at the beginning of the value
            execute_shorthand(ci, 'l')
            assert not ci.in_foreground #At the beginning of the value

        with patch.object(ci, 'idle_loop', side_effect=scenario) as p:
            return_value = ci.activate()
        assert return_value is None

    def test_entering_value(self):
        ci = CharArrowKeysInput(get_mock_input(), get_mock_output(), name=ci_name)
        ci.refresh = lambda *args, **kwargs: None

        expected_output = "hello"
        test_key_offsets = (8, 5, 12, 12, 15)
        test_keys = "r".join(["u"*offset for offset in test_key_offsets])
        test_keys += "e" #Press ENTER

        def scenario():
            for key in test_keys:
                execute_shorthand(ci, key)
            assert not ci.in_foreground  # Should exit on last "e"

        with patch.object(ci, 'idle_loop', side_effect=scenario) as p:
            return_value = ci.activate()
        assert return_value == expected_output

    def test_entering_value_with_backspaces(self):
        ci = CharArrowKeysInput(get_mock_input(), get_mock_output(), name=ci_name)
        ci.refresh = lambda *args, **kwargs: None

        expected_output = "hello"
        test_key_offsets = (8, 5, 12, 12, 15)
        test_keys = "r".join(["u"*offset for offset in test_key_offsets])
        test_keys += "d"*(test_key_offsets[-1]+1) #Going back to the backspace character
        test_keys += "lr" #should erase the latest character and go to the position it took
        test_keys += "u"*test_key_offsets[-1] #adding the latest character again
        test_keys += "e" #Press ENTER

        def scenario():
            for key in test_keys:
                execute_shorthand(ci, key)
            assert not ci.in_foreground  # Should exit on last "e"

        with patch.object(ci, 'idle_loop', side_effect=scenario) as p:
            return_value = ci.activate()
        assert return_value == expected_output

    def test_shows_data_on_screen(self):
        """Tests whether the CharArrowKeysInput outputs data on screen when it's ran"""
        i = get_mock_input()
        o = get_mock_output()
        ci = CharArrowKeysInput(i, o, message="Test:", name=ci_name)

        expected_output = "hello"
        test_key_offsets = (8, 5, 12, 12, 15)
        test_keys = "r".join(["u"*offset for offset in test_key_offsets])
        test_keys += "e" #Press ENTER

        def scenario():
            assert o.display_data.called
            assert o.display_data.call_args[0] == ('Test:', '')
            for key in test_keys:
                execute_shorthand(ci, key)
            assert not ci.in_foreground  # Should exit on last "e"

        with patch.object(ci, 'idle_loop', side_effect=scenario) as p:
            ci.activate()
            #The scenario should only be called once
            assert ci.idle_loop.called
            assert ci.idle_loop.call_count == 1

        assert o.display_data.called
        assert o.display_data.call_count == len(test_keys) #Magically, it's the same
        assert o.display_data.call_args[0] == ('Test:', 'hello')

if __name__ == '__main__':
    unittest.main()
