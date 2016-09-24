from time import sleep
from copy import copy
import logging

from threading import Event

def to_be_foreground(func): #A safety check wrapper so that certain functions don't get called if refresher is not the one active
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            print(func.__name__)
    return wrapper

class Refresher():
    """Implements a state where display is refreshed from time to time, updating the screen with information from a function.
    """
    refresh_function = None
    refresh_interval = 0
    display_callback = None
    in_background = Event()
    in_foreground = False
    name = ""
    keymap = None

    def __init__(self, refresh_function, i, o, refresh_interval=1, keymap={}, name="Refresher"):
        """Initialises the Refresher object.
        
        Args:

            * ``refresh_function``: a function which returns data to be displayed on the screen upon being called, in the format accepted by ``screen.display_data()``
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``keymap``: Keymap entries you want to set while Refresher is active
            * ``name``: Refresher name which can be used internally and for debugging.

        """
        self.i = i
        self.o = o
        self.name = name
        self.refresh_interval = refresh_interval
        self.refresh_function = refresh_function
        self.set_keymap(keymap)
        self.set_display_callback(self.o.display_data)

    def to_foreground(self):
        """ Is called when refresher's ``activate()`` method is used, sets flags and performs all the actions so that refresher can display its contents and receive keypresses."""
        logging.info("menu {0} enabled".format(self.name))    
        self.in_background.set()
        self.in_foreground = True
        self.refresh()
        self.activate_keymap()

    @to_be_foreground
    def to_background(self):
        """ Signals ``activate`` to finish executing """
        self.in_foreground = False
        logging.info("menu {0} disabled".format(self.name))    

    def activate(self):
        """ A method which is called when refresher needs to start operating. Is blocking, sets up input&output devices, renders the refresher, periodically calls the refresh function&refreshes the screen while self.in_foreground is True, while refresher callbacks are executed from the input device thread."""
        logging.info("menu {0} activated".format(self.name))    
        self.to_foreground() 
        sleep_time = 0.1
        counter = 0
        rts_ratio = self.refresh_interval/sleep_time
        while self.in_background.isSet(): 
            if self.in_foreground:
                if counter == rts_ratio:
                    counter = 0
                if counter == 0:
                    self.refresh()
                counter += 1
            sleep(sleep_time)
        logging.debug(self.name+" exited")
        return True

    def deactivate(self):
        """ Deactivates the refresher completely, exiting it."""
        self.in_foreground = False
        self.in_background.clear()
        logging.info("menu {0} deactivated".format(self.name))    

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which refresher is currently active. """
        logging.info("Active menu is {0}".format(self.name))    

    def process_callback(self, function):
        """ Decorates a function to be used by Refresher element.
        |Is typically used as a wrapper for a callback from input event processing thread.
        |After callback's execution is finished, sets the keymap again and refreshes the refresher."""
        def wrapper(*args, **kwargs):
            self.to_background() 
            function(*args, **kwargs)
            self.to_foreground() 
        return wrapper

    def process_keymap(self, keymap):
        """Sets the keymap. In future, will allow per-system keycode-to-callback tweaking using a config file. """
        for key in keymap:
            callback = self.process_callback(keymap[key])
            keymap[key] = callback
        keymap["KEY_LEFT"] = lambda: self.deactivate()
        return keymap

    def set_keymap(self, keymap):
        """Generate and sets the input device's keycode-to-callback mapping. Re-starts the input device because of passing-variables-between-threads issues."""
        self.keymap = self.process_keymap(keymap)

    @to_be_foreground
    def activate_keymap(self):
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.listen()

    @to_be_foreground
    def refresh(self):
        logging.debug("{0}: refreshed data on display".format(self.name))
        self.display_callback(*self.refresh_function())

    def set_display_callback(self, callback):
        logging.debug("{0}: display callback set".format(self.name))
        self.display_callback = callback

