"""tests for Refresher"""
import os
import unittest

from mock import patch, Mock


try:
    from ui import Refresher
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
        from refresher import Refresher


def get_mock_input():
    return Mock()


def get_mock_output(rows=8, cols=21):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols, type=["char"])
    return m


r_name = "Test Refresher"


class TestRefresher(unittest.TestCase):
    """Tests the Refresher class"""

    def test_constructor(self):
        """Tests constructor"""
        r = Refresher(lambda: "Hello", get_mock_input(), get_mock_output(), name=r_name)
        self.assertIsNotNone(r)

    def test_keymap(self):
        """Tests the keymap entries"""
        r = Refresher(lambda: "Hello", get_mock_input(), get_mock_output(), name=r_name)
        self.assertIsNotNone(r.keymap)
        for key_name, callback in r.keymap.iteritems():
            self.assertIsNotNone(callback)

    def test_exit_label_leakage(self):
        """tests whether the keymaps (and keymap entries) of different Refresher leak one into another"""
        i = get_mock_input()
        o = get_mock_output()
        r1 = Refresher(lambda: "Hello", i, o, name=r_name + "1", keymap={"KEY_LEFT":lambda: True})
        r2 = Refresher(lambda: "Hello", i, o, name=r_name + "2", keymap={"KEY_LEFT":lambda: False})
        r3 = Refresher(lambda: "Hello", i, o, name=r_name + "3")
        assert (r1.keymap != r2.keymap)
        assert (r1.keymap["KEY_LEFT"] != r2.keymap["KEY_LEFT"])
        assert (r2.keymap != r3.keymap)
        assert (r2.keymap["KEY_LEFT"] != r3.keymap["KEY_LEFT"])
        assert (r1.keymap != r3.keymap)
        assert (r1.keymap["KEY_LEFT"] != r3.keymap["KEY_LEFT"])

    def test_left_key_exits(self):
        r = Refresher(lambda: "Hello", get_mock_input(), get_mock_output(), name=r_name)
        r.refresh = lambda *args, **kwargs: None

        # This test doesn't actually test whether the Refresher exits
        # It only tests whether the in_foreground attribute is set
        # Any ideas? Maybe use some kind of "timeout" library?
        def scenario():
            r.keymap["KEY_LEFT"]()
            assert not r.in_foreground
            # If the test fails, either the assert will trigger a test failure,
            # or the idle loop will just run indefinitely
            # The exception thrown should protect from the latter
            raise KeyboardInterrupt

        with patch.object(r, 'idle_loop', side_effect=scenario) as p:
            try:
                r.activate()
            except KeyboardInterrupt:
                pass #Test succeeded

    def test_shows_data_on_screen(self):
        """Tests whether the Refresher outputs data on screen when it's ran"""
        i = get_mock_input()
        o = get_mock_output()
        r = Refresher(lambda: "Hello", i, o, name=r_name)

        def scenario():
            r.refresh()
            r.deactivate()

        with patch.object(r, 'idle_loop', side_effect=scenario) as p:
            r.activate()
            #The scenario should only be called once
            assert r.idle_loop.called
            assert r.idle_loop.call_count == 1

        assert o.display_data.called
        assert o.display_data.call_count == 2 #One in to_foreground, and one in patched idle_loop
        assert o.display_data.call_args_list[0][0] == ("Hello", )
        assert o.display_data.call_args_list[1][0] == ("Hello", )


if __name__ == '__main__':
    unittest.main()
