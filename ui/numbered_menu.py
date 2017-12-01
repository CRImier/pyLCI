from ui import Menu
from ui.base_list_ui import BaseListUIElement
from ui.utils import clamp


class UIWidget(object):
    pass  # todo : complete


class NumberedMenu(UIWidget, Menu):
    """
    todo: options:
    - activate entry after type or select only
    - delay for keypresses
    """

    def __init__(self, *args, **kwargs):
        Menu.__init__(self, *args, **kwargs)
        self.key_map = {
            "KEY_1": 1,
            "KEY_2": 2,
            "KEY_3": 3,
            "KEY_4": 4,
            "KEY_5": 5,
            "KEY_6": 6,
            "KEY_7": 7,
            "KEY_8": 8,
            "KEY_9": 9,
            "KEY_0": 0,
        }

    def activate(self):
        self.i.set_streaming(self.on_key_pressed)
        Menu.activate(self)

    def deactivate(self):
        Menu.deactivate(self)
        self.i.remove_streaming()

    def on_key_pressed(self, key):
        if key not in self.key_map.keys(): return
        self.pointer = clamp(self.key_map[key], 0, len(self.contents) - 1)
        self.view.refresh()

    def process_contents(self):
        BaseListUIElement.process_contents(self)

        # adding a number in front of the entry name
        self.contents = [["{} {}".format(index, entry[0]), entry[1]] for index, entry in enumerate(self.contents)]
