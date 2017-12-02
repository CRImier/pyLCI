from threading import Lock
from time import sleep, time

from ui import Menu
from ui.utils import clamp, check_value_lock, to_be_foreground


class UIWidget(object):
    pass  # todo : complete


class NumberedMenu(UIWidget, Menu):
    """
    This subclass of Menu allows the user to navigate using the keypad in the menu. If the menu is 10 entries or less
    the navigation is instant. If it has more than 10, it let's the user type multiple digits to navigate.

    The `input_delay` parameter controls how long the menu waits before considering an input as definitive.
    If `input_delay` is 0, then only the 10 first entries are considered navigable with the keypad.

    The `prepend_numbers` parameters controls whether the entries should be prefixed by their number.
    The default value is `True`
    """
    def __init__(self, *args, **kwargs):
        self.prepend_numbers = kwargs.pop('prepend_numbers') if 'prepend_numbers' in kwargs else True
        self.input_delay = kwargs.pop('input_delay') if 'input_delay' in kwargs else 1
        Menu.__init__(self, *args, **kwargs)
        self.value_lock = Lock()
        self.custom_key_map = {
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
        self.entry_count = len(self.contents)
        self.last_input_time = 0
        self.current_input = None

    def activate(self):
        self.set_keymap()
        # self.i.set_streaming(self.on_key_pressed)
        self.before_activate()
        self.to_foreground()
        if not self.is_multi_digit():
            # Menu.activate(self)  # no need to check for character state since we are in instant mode
            return

        self.last_input_time = -self.input_delay
        while self.in_background:  # Most of the work is done in input callbacks
            sleep(0.1)
            self.idle_loop()
            self.check_character_state()

    def set_keymap(self):
        Menu.set_keymap(self)
        self.i.set_streaming(self.on_key_pressed)

    def deactivate(self):
        Menu.deactivate(self)
        self.i.remove_streaming()

    @to_be_foreground
    def on_key_pressed(self, key):
        if key == "KEY_RIGHT" and self.is_multi_digit():
            self.confirm_current_input()

        if key not in self.custom_key_map: return
        if self.is_multi_digit():
            self.process_multi_digit_input(key)
        else:
            self.process_single_digit_input(key)
        self.view.refresh()

    def process_single_digit_input(self, key):
        print('single')
        self.move_to_entry(self.custom_key_map[key])

    def process_multi_digit_input(self, key):
        self.last_input_time = time()
        if not self.current_input:
            self.current_input = str(self.custom_key_map[key])
        else:
            self.current_input += str(self.custom_key_map[key])

    def move_to_entry(self, index):
        self.pointer = clamp(index, 0, len(self.contents) - 1)
        self.current_input = None
        self.view.refresh()

    def process_contents(self):
        Menu.process_contents(self)
        if self.prepend_numbers:
            self.prepend_entry_text()

    def prepend_entry_text(self):
        # prepend numbers to each entry name
        has_exit_entry = self.exit_entry in self.contents
        if self.is_multi_digit():  # prepend 10 first only
            self.contents = [["{} {}".format(i, e[0]), e[1]] for i, e in enumerate(self.contents) if
                             e is not self.exit_entry]

        else:  # prepend all entries
            content = []
            for i, e in enumerate(self.contents):
                if i < 10:
                    content.append(["{} {}".format(i, e[0]), e[1]])
                else:
                    content.append([e[0], e[1]])
            self.contents = content
        if has_exit_entry:
            self.contents.append(self.exit_entry)

    @check_value_lock
    def check_character_state(self):
        if self.is_current_input_finished():
            self.move_to_entry(int(self.current_input))

    def is_multi_digit(self):
        return self.input_delay > 0

    def is_current_input_finished(self):
        # nothing in the buffer
        if not self.current_input:
            return False

        # no need to let the user input '100' if we have 20 entries
        if len(str(self.current_input)) == len(str(self.entry_count)):
            return True

        # user typed 17 and we have 12 entries
        if int(self.current_input) >= self.entry_count:
            return True

        now = time()
        elapsed = now - self.last_input_time
        if self.is_multi_digit() and elapsed >= self.input_delay:  # delay wait is over
            return True
        return False

    def confirm_current_input(self):
        if self.current_input is None:
            return
        self.move_to_entry(int(self.current_input))
