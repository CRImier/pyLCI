import logging
from threading import Event
from time import sleep

from ui.utils import to_be_foreground

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Refresher(object):
    """Implements a state where display is refreshed from time to time, updating the screen with information from a function.
    """
    refresh_function = None
    refresh_interval = 0
    display_callback = None
    in_foreground = False
    name = ""
    keymap = None

    def __init__(self, refresh_function, i, o, refresh_interval=1, keymap=None, name="Refresher"):
        """Initialises the Refresher object.
        
        Args:

            * ``refresh_function``: a function which returns data to be displayed on the screen upon being called, in the format accepted by ``screen.display_data()``
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``refresh_interval``: Time between display refreshes (and, accordingly, ``refresh_function`` calls)
            * ``keymap``: Keymap entries you want to set while Refresher is active
            * ``name``: Refresher name which can be used internally and for debugging.

        """
        self.i = i
        self.o = o
        self.name = name
        self.refresh_interval = refresh_interval
        self.refresh_function = refresh_function
        self.set_keymap(keymap if keymap else {})
        self.in_background = Event()

    def to_foreground(self):
        """ Is called when refresher's ``activate()`` method is used, sets flags and performs all the actions so that refresher can display its contents and receive keypresses."""
        logger.debug("refresher {0} in foreground".format(self.name))    
        self.in_background.set()
        self.in_foreground = True
        self.refresh()
        self.activate_keymap()

    def to_background(self):
        """ Signals ``activate`` to finish executing """
        self.in_foreground = False
        logger.debug("refresher {0} in background".format(self.name))

    def activate(self):
        """ A method which is called when refresher needs to start operating. Is blocking, sets up input&output devices, renders the refresher, periodically calls the refresh function&refreshes the screen while self.in_foreground is True, while refresher callbacks are executed from the input device thread."""
        logger.debug("refresher {0} activated".format(self.name))
        self.to_foreground() 
        counter = 0
        divisor = 20.0
        sleep_time = self.refresh_interval/divisor
        while self.in_background.isSet(): 
            if self.in_foreground:
                if counter == divisor:
                    counter = 0
                if counter == 0:
                    self.refresh()
                counter += 1
            sleep(sleep_time)
        logger.debug(self.name+" exited")
        return True

    def deactivate(self):
        """ Deactivates the refresher completely, exiting it."""
        self.in_foreground = False
        self.in_background.clear()
        logger.debug("refresher {0} deactivated".format(self.name))

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which refresher is currently active. """
        logger.debug("Active refresher is {0}".format(self.name))

    def process_callback(self, func):
        """ Decorates a function to be used by Refresher element.
        |Is typically used as a wrapper for a callback from input event processing thread.
        |After callback's execution is finished, sets the keymap again and refreshes the refresher."""
        def wrapper(*args, **kwargs):
            self.to_background() 
            func(*args, **kwargs)
            logger.debug("Executed wrapped function: {}".format(func.__name__))
            if self.in_background.isSet():
                self.to_foreground() 
        wrapper.__name__ == func.__name__
        return wrapper

    def process_keymap(self, keymap):
        """Sets the keymap. In future, will allow per-system keycode-to-callback tweaking using a config file. """
        logger.debug("{}: processing keymap - {}".format(self.name, keymap))
        for key in keymap:
            callback = self.process_callback(keymap[key])
            keymap[key] = callback
        if not "KEY_LEFT" in keymap:
            keymap["KEY_LEFT"] = self.deactivate
        #if not "KEY_RIGHT" in keymap and:
        #    keymap["KEY_RIGHT"] = self.print_name
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
        logger.debug("{0}: refreshed data on display".format(self.name))
        data_to_display = self.refresh_function()
        if isinstance(data_to_display, basestring):
            #Passed a string, not a list.
            #Let's be user-friendly and wrap it in a list!
            data_to_display = [data_to_display]
        elif isinstance(data_to_display, tuple):
            #Passed a tuple. Let's convert it into a list!
            data_to_display = list(data_to_display)
        elif not isinstance(data_to_display, list):
            raise ValueError("refresh_function returned an unsupported type: {}!".format(type(data_to_display)))
        self.o.display_data(*data_to_display)
