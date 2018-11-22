"""test for Overlays"""
import os
import unittest

from mock import patch, Mock

try:
    from ui import Menu, HelpOverlay
    from ui.base_list_ui import Canvas
    fonts_dir = "ui/fonts"
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
        from overlays import HelpOverlay
        from menu import Menu
        from base_list_ui import Canvas
        fonts_dir = "../fonts"

def get_mock_input():
    return Mock()

def get_mock_output(rows=8, cols=21):
    m = Mock()
    m.configure_mock(rows=rows, cols=cols, type=["char"])
    return m

def get_mock_graphical_output(width=128, height=64, mode="1", cw=6, ch=8):
    m = get_mock_output(rows=width/cw, cols=height/ch)
    m.configure_mock(width=width, height=height, device_mode=mode, char_height=ch, char_width=cw, type=["b&w-pixel"])
    return m

mu_name = "Overlay test menu"


class Testoverlays(unittest.TestCase):
    """tests menu class"""

    def test_ho_constructor(self):
        """tests constructor"""
        overlay = HelpOverlay(lambda: True)
        self.assertIsNotNone(overlay)

    def test_ho_apply(self):
        overlay = HelpOverlay(lambda: True)
        mu = Menu([], get_mock_input(), get_mock_output(), name=mu_name, config={})
        overlay.apply_to(mu)
        self.assertIsNotNone(overlay)
        self.assertIsNotNone(mu)

    def test_ho_push_pop_callback(self):
        cb1 = lambda:True
        cb2 = lambda:False
        overlay = HelpOverlay(cb1)
        assert(overlay.get_key_and_callback()[1] == cb1)
        overlay.push_callback(cb2)
        assert(overlay.get_key_and_callback()[1] == cb2)
        overlay.pop_callback()
        assert(overlay.get_key_and_callback()[1] == cb1)

    def test_ho_text_redraw(self):
        overlay = HelpOverlay(lambda: True)
        mu = Menu([["Hello"]], get_mock_input(), get_mock_output(), name=mu_name, config={})
        overlay.apply_to(mu)
        def scenario():
            mu.deactivate()
            assert not mu.in_foreground

        with patch.object(mu, 'idle_loop', side_effect=scenario) as p:
            mu.activate()
        assert mu.o.display_data.called
        assert mu.o.display_data.call_count == 1 #One in to_foreground
        assert mu.o.display_data.call_args[0] == ('Hello', 'Back')

    def test_ho_graphical_redraw(self):
        o = get_mock_graphical_output()
        overlay = HelpOverlay(lambda: True)
        mu = Menu([], get_mock_input(), o, name=mu_name, config={})
        Canvas.fonts_dir = fonts_dir
        overlay.apply_to(mu)
        # Exiting immediately, but we should get at least one redraw
        def scenario():
            mu.deactivate()  # KEY_LEFT
            assert not mu.in_foreground

        with patch.object(mu, 'idle_loop', side_effect=scenario) as p:
            mu.activate()
        assert o.display_image.called
        assert o.display_image.call_count == 1 #One in to_foreground

    def test_ho_graphical_icon_disappears(self):
        o = get_mock_graphical_output()
        overlay = HelpOverlay(lambda: True)
        mu = Menu([], get_mock_input(), o, name=mu_name, config={})
        mu.idle_loop = lambda *a, **k: True
        Canvas.fonts_dir = fonts_dir
        overlay.apply_to(mu)
        def activate():
            mu.before_activate()
            mu.to_foreground()
            mu.idle_loop()
            img_1 = o.display_image.call_args[0]
            mu.idle_loop()
            mu.refresh()
            img_2 = o.display_image.call_args[0]
            assert(img_1 == img_2)
            for i in range(overlay.duration):
                mu.idle_loop()
            mu.refresh()
            img_2 = o.display_image.call_args[0]
            assert(img_1 != img_2)
            mu.deactivate()  # KEY_LEFT

        with patch.object(mu, 'activate', side_effect=activate) as p:
            mu.activate()


if __name__ == '__main__':
    unittest.main()
