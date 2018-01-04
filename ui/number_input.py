from time import sleep
from copy import copy
from helpers import setup_logger
logger = setup_logger(__name__, "warning")

from ui.utils import to_be_foreground


class IntegerAdjustInput(object):
    """Implements a simple number input dialog which allows you to increment/decrement a number using  which can be used to navigate through your application, output a list of values or select actions to perform. Is one of the most used elements, used both in system core and in most of the applications.

    Attributes:

    * ``number``: The number being changed.
    * ``initial_number``: The number sent to the constructor. Used by reset() method.
    * ``selected_number``: A flag variable to be returned by activate().
    * ``in_foreground`` : a flag which indicates if UI element is currently displayed. If it's not active, inhibits any of element's actions which can interfere with other UI element being displayed.

    """
    display_callback = None
    in_foreground = False
    name = ""
    message = ""
    initial_number = 0
    number = 0
    selected_number = None

    def __init__(self, number, i, o, message="Pick a number:", interval=1, name="IntegerAdjustInput"):
        """Initialises the IntegerAdjustInput object.
        
        Args:

            * ``number``: number to be operated on
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``message``: Message to be shown on the first line of the screen when UI element is active.
            * ``interval``: Value by which the number is incremented and decremented.
            * ``name``: UI element name which can be used internally and for debugging.

        """
        self.i = i
        self.o = o
        if type(number) != int:
            raise ValueError("IntegerAdjustInput operates on integers!")
        self.initial_number = number
        self.number = number
        self.message = message
        self.name = name
        self.interval = interval
        self.set_display_callback(o.display_data)
        self.generate_keymap()

    def to_foreground(self):
        """ Is called when ``activate()`` method is used, sets flags and performs all the actions so that UI element can display its contents and receive keypresses. Also, refreshes the screen."""
        logger.info("{0} enabled".format(self.name))    
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        """ A method which is called when input element needs to start operating. Is blocking, sets up input&output devices, renders the UI element and waits until self.in_background is False, while callbacks are executed from the input device thread.
        This method returns the selected number if KEY_ENTER was pressed, thus accepting the selection.
        This method returns None when the UI element was exited by KEY_LEFT and thus it's assumed changes to the number were not accepted."""
        logger.info("{0} activated".format(self.name))    
        self.to_foreground() 
        while self.in_foreground: #All the work is done in input callbacks
            sleep(0.1)
        logger.debug(self.name+" exited")
        return self.selected_number

    def deactivate(self):
        """ Deactivates the UI element, exiting it and thus making activate() return."""
        self.in_foreground = False
        logger.info("{0} deactivated".format(self.name))    

    def print_number(self):
        """ A debug method. Useful for hooking up to an input event so that you can see current number value. """
        logger.info(self.number)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which UI element is currently processing input events. """
        logger.info("{0} active".format(self.name))    

    @to_be_foreground
    def decrement(self):
        """Decrements the number by selected ``interval``"""
        self.number -= self.interval
        self.refresh()    

    @to_be_foreground
    def increment(self):
        """Increments the number by selected ``interval``"""
        self.number += self.interval
        self.refresh()    

    @to_be_foreground
    def reset(self):
        """Resets the number, setting it to the number passed to the constructor."""
        logger.debug("Number reset")
        self.number = self.initial_number
        self.refresh()    

    @to_be_foreground
    def select_number(self):
        """Selects the currently active number value, making activate() return it."""
        logger.debug("Number accepted")
        self.selected_number = self.number
        self.deactivate()

    @to_be_foreground
    def exit(self):
        """Exits discarding all the changes to the number."""
        logger.debug("{} exited without changes".format(self.name))
        self.deactivate()

    def generate_keymap(self):
        self.keymap = {
        "KEY_RIGHT":lambda: self.reset(),
        "KEY_UP":lambda: self.increment(),
        "KEY_DOWN":lambda: self.decrement(),
        "KEY_KPENTER":lambda: self.select_number(),
        "KEY_ENTER":lambda: self.select_number(),
        "KEY_LEFT":lambda: self.exit()
        }

    @to_be_foreground
    def set_keymap(self):
        self.generate_keymap()
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.listen()

    def get_displayed_data(self):
        return [self.message, str(self.number).rjust(self.o.cols)]

    @to_be_foreground
    def refresh(self):
        logger.debug("{0}: refreshed data on display".format(self.name))
        self.display_callback(*self.get_displayed_data())

    def set_display_callback(self, callback):
        logger.debug("{0}: display callback set".format(self.name))
        self.display_callback = callback

