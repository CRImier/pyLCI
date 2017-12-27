
from threading import Event
from time import sleep

import PIL

from helpers import setup_logger
from ui.utils import to_be_foreground

logger = setup_logger(__name__, "info")


class Refresher(object):
    """
    A Refresher allows you to update the screen on a regular interval.
    All you need is to provide a function that'll return the text/image you want to display;
    that function will then be called with the desired frequency and the display
    will be updated with whatever it returns.
    """

    def __init__(self, refresh_function, i, o, refresh_interval=1, keymap=None, name="Refresher"):
        """Initialises the Refresher object.
        
        Args:

            * ``refresh_function``: a function which returns data to be displayed on the screen upon being called, in the format accepted by ``screen.display_data()`` or ``screen.display_image()``. To be exact, supported return values are:

              * Tuples and lists - are converted to lists and passed to ``display_data()``
              * Strings - are converted to a single-element list and passed to ``display_data()``
              * `PIL.Image` objects - are passed to ``display_image()``

            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``refresh_interval``: Time between display refreshes (and, accordingly, ``refresh_function`` calls). Refresh intervals less than 0.1 second are not supported.
            * ``keymap``: Keymap entries you want to set while Refresher is active. By default, KEY_LEFT deactivates the Refresher, if you wan tto override it, do it carefully.
            * ``name``: Refresher name which can be used internally and for debugging.

        """
        self.i = i
        self.o = o
        self.name = name
        self.refresh_interval = refresh_interval
        self.refresh_function = refresh_function
        #interval for checking the in_background property in the activate()
        self.sleep_time = 0.1
        self.calculate_intervals()
        self.set_keymap(keymap if keymap else {})
        self.in_foreground = False
        self.in_background = Event()

    def to_foreground(self):
        """ Is called when refresher's ``activate()`` method is used, sets flags and performs all the actions so that refresher can display its contents and receive keypresses."""
        logger.debug("refresher {} in foreground".format(self.name))
        self.in_background.set()
        self.in_foreground = True
        self.refresh()
        self.activate_keymap()

    def to_background(self):
        """ Signals ``activate`` to finish executing """
        self.in_foreground = False
        logger.debug("refresher {} in background".format(self.name))

    def activate(self):
        """ A method which is called when refresher needs to start operating. Is blocking, sets up input&output devices, renders the refresher, periodically calls the refresh function&refreshes the screen while self.in_foreground is True, while refresher callbacks are executed from the input device thread."""
        logger.debug("refresher {} activated".format(self.name))
        self.to_foreground()
        while self.in_background.isSet():
            self.idle_loop()
        logger.debug(self.name+" exited")
        return True

    def calculate_intervals(self):
        #in_background of the refresher needs to be checked approx. each 0.1 second,
        #since users expect the refresher to exit almost instantly
        self.iterations_before_refresh = self.refresh_interval/self.sleep_time
        if self.iterations_before_refresh < 1:
            self.iterations_before_refresh = 1
        else:
            self.iterations_before_refresh = int(self.iterations_before_refresh)
        self.counter = 0

    def idle_loop(self):
        if self.in_foreground:
            if self.counter == self.iterations_before_refresh:
                self.counter = 0
            if self.counter == 0:
                self.refresh()
            self.counter += 1
        sleep(self.sleep_time)

    def deactivate(self):
        """ Deactivates the refresher completely, exiting it."""
        self.in_foreground = False
        self.in_background.clear()
        logger.debug("refresher {} deactivated".format(self.name))

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which refresher is currently active. """
        logger.debug("Active refresher is {}".format(self.name))

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
        """Processes the keymap. In future, will allow per-system keycode-to-callback tweaking using a config file. """
        logger.debug("{}: processing keymap - {}".format(self.name, keymap))
        for key in keymap:
            callback = self.process_callback(keymap[key])
            keymap[key] = callback
        if not "KEY_LEFT" in keymap:
            keymap["KEY_LEFT"] = self.deactivate
        return keymap

    def set_keymap(self, keymap):
        """Sets the refresher's keymap (filtered using ``process_keymap`` before setting)."""
        self.keymap = self.process_keymap(keymap)

    @to_be_foreground
    def activate_keymap(self):
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.listen()

    @to_be_foreground
    def refresh(self):
        logger.debug("{}: refreshed data on display".format(self.name))
        data_to_display = self.refresh_function()
        if isinstance(data_to_display, basestring):
            #Passed a string, not a list.
            #Let's be user-friendly and wrap it in a list!
            data_to_display = [data_to_display]
        elif isinstance(data_to_display, tuple):
            #Passed a tuple. Let's convert it into a list!
            data_to_display = list(data_to_display)
        elif isinstance(data_to_display, PIL.Image.Image):
            if "b&w-pixel" not in self.o.type:
                raise ValueError("The screen doesn't support showing images!")
            self.o.display_image(data_to_display)
            return
        elif not isinstance(data_to_display, list):
            raise ValueError("refresh_function returned an unsupported type: {}!".format(type(data_to_display)))
        self.o.display_data(*data_to_display)
