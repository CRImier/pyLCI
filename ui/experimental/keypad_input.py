from time import sleep
from math import ceil
import logging


def to_be_foreground(func): #A safety check wrapper so that certain checks don't get called if menu is not the one active
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

class NumberKeypadInputLayer():
    """Experimental UI element. Suited for multi-row screens, not tested on and developed for 2x16 and no cursor implemented yet.

    Implements a number input UI element for a numeric keypad, allowing to translate keycodes directly into numbers.

    Attributes:

    * ``value``: currently entered number string.
    * ``in_foreground``: A flag which indicates if UI element is currently displayed. If it's not active, inhibits any of element's actions which can interfere with other UI element being displayed.

    """
    
    allowed_chars = '0123456789*#'
     
    in_foreground = False
    value = ""

    def __init__(self, i, o, message="Input number:", keymap=None, name="CharArrowKeysInput"):
        """Initialises the CharArrowKeysInput object.
        
        Args:

            * ``i``, ``o``: input&output device objects

        """
        self.i = i
        self.o = o
        self.message = message
        self.name = name
        self.keymap = keymap if keymap else {}
        self.generate_keymap()

    def to_foreground(self):
        """ Is called when ``activate()`` method is used, sets flags and performs all the actions so that UI element can display its contents and receive keypresses. Also, refreshes the screen."""
        logging.info("{0} enabled".format(self.name))    
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        """ A method which is called when input element needs to start operating. Is blocking, sets up input&output devices, renders the element and waits until self.in_background is False, while menu callbacks are executed from the input device thread.
        This method returns the selected value if KEY_ENTER was pressed, thus accepting the selection.
        This method returns None when the UI element was exited by KEY_LEFT and thus the value was not accepted. """
        logging.info("{0} activated".format(self.name))    
        self.to_foreground() 
        while self.in_foreground: #All the work is done in input callbacks
            sleep(0.1)
        self.i.remove_streaming()
        logging.debug(self.name+" exited")
        return self.value

    def deactivate(self):
        """ Deactivates the UI element, exiting it and thus making activate() return."""
        self.in_foreground = False
        logging.info("{0} deactivated".format(self.name))    

    def process_keycode(self, key_name, *args):
        header = "KEY_"
        name = key_name[len(header):]
        if name in self.allowed_chars:
            self.value += name
            self.refresh()

    def backspace(self):
        self.value = self.value[:-1]
        self.refresh()

    def print_value(self):
        """ A debug method. Useful for hooking up to an input event so that you can see current value. """
        logging.info(self.value)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which UI element is currently processing input events. """
        logging.info("{0} active".format(self.name))    

    def generate_keymap(self):
        for key in self.keymap:
            if isinstance(self.keymap[key], list):
                callback = self.keymap[key][0]
                arguments = self.keymap[key][1:]
                self.keymap[key] = self.wrap_external( lambda: callback( *(getattr(self, arg_str) for arg_str in arguments) ) )
        self.keymap.update({
        "KEY_F1":lambda: self.deactivate(),
        "KEY_F2":lambda: self.backspace()
        })

    @to_be_foreground
    def set_keymap(self):
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.set_keymap(self.keymap)
        self.i.set_streaming(self.process_keycode)
        self.i.listen()

    def wrap_external(self, func):
        def wrapper(*args, **kwargs):
            rvalue = func(*args, **kwargs)
            self.set_keymap()
            self.refresh()
            return rvalue
        return wrapper

    def get_displayed_data(self):
        """Experimental: not meant for 2x16 displays
        
        Formats the value and the message to show it on the screen, then returns a list that can be directly used by o.display_data"""
        displayed_data = [self.message]
        screen_rows = self.o.rows
        screen_cols = self.o.cols
        static_line_count = 2 #One for message, another for context key labels
        lines_taken_by_value = int(ceil( float(len(self.value)) / (screen_rows-static_line_count) ))
        for line_i in range(lines_taken_by_value):
            displayed_data.append(self.value[(line_i*screen_cols):][:screen_cols])
        for _ in range( screen_rows - (static_line_count + lines_taken_by_value) ):
            displayed_data.append("") #Just empty line
        half_line_length = screen_cols/2
        last_line = "Cancel".center(half_line_length) + "Erase".center(half_line_length)
        displayed_data.append(last_line)
        return displayed_data

    @to_be_foreground
    def refresh(self):
        self.o.display_data(*self.get_displayed_data())
        logging.debug("{}: refreshed data on display".format(self.name))
