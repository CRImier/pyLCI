from threading import Event
from time import sleep

import PIL

from helpers import setup_logger
from ui.utils import to_be_foreground
from number_input import IntegerAdjustInput

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

            * ``refresh_interval``: Time between display refreshes (and, accordingly, ``refresh_function`` calls).
            * ``keymap``: Keymap entries you want to set while Refresher is active.
              * If set to a string
              * By default, KEY_LEFT deactivates the Refresher, if you want to override it, make sure that user can still exit the Refresher.
            * ``name``: Refresher name which can be used internally and for debugging.

        """
        self.i = i
        self.o = o
        self.name = name
        self.set_refresh_interval(refresh_interval)
        self.refresh_function = refresh_function
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

    def pause(self):
        """
        Pauses the refresher, not allowing it to print anything on the screen
        while it's paused.
        """
        self.in_foreground = False

    def resume(self):
        """
        Resumes the refresher after it's been paused, allowing it to continue
        printing things on the screen. Refreshes the screen when it's called.
        """
        self.in_foreground = True
        self.activate_keymap()
        self.refresh()

    def set_refresh_interval(self, new_interval):
        """Allows setting Refresher's refresh intervals after it's been initialized"""
        #interval for checking the in_background property in the activate()
        #when refresh_interval is small enough, is the same as refresh_interval
        self.refresh_interval = new_interval
        self.sleep_time = 0.1 if new_interval > 0.1 else new_interval
        self.calculate_intervals()

    def calculate_intervals(self):
        """Calculates the sleep intervals of the refresher, so that no matter the
        ``refresh_interval``, the refresher is responsive. Also, sets the counter to zero."""
        #in_background of the refresher needs to be checked approx. each 0.1 second,
        #since users expect the refresher to exit almost instantly
        iterations_before_refresh = self.refresh_interval/self.sleep_time
        if iterations_before_refresh < 1:
            logger.warning("{}: self.refresh_interval is smaller than self.sleep_time!".format(self.name))
            #Failsafe
            self.iterations_before_refresh = 1
        else:
            self.iterations_before_refresh = int(iterations_before_refresh)
        self._counter = 0

    def idle_loop(self):
        if self.in_foreground:
            if self._counter == self.iterations_before_refresh:
                self._counter = 0
            if self._counter == 0:
                self.refresh()
            self._counter += 1
        sleep(self.sleep_time)

    def deactivate(self):
        """ Deactivates the refresher completely, exiting it."""
        self.in_foreground = False
        self.in_background.clear()
        logger.debug("refresher {} deactivated".format(self.name))

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which refresher is currently active. """
        logger.debug("Active refresher is {}".format(self.name))

    def change_interval(self):
        """
        A helper function to adjust the Refresher's refresh interval while it's running
        """
        new_interval = IntegerAdjustInput(self.refresh_interval, i, o, message="Refresh interval:").activate()
        if new_interval is not None:
            self.set_refresh_interval(new_interval)

    def process_callback(self, func):
        """ Decorates a function to be used by Refresher element.
        |Is typically used as a wrapper for a callback from input event processing thread.
        |After callback's execution is finished, sets the keymap again and refreshes the refresher."""
        def wrapper(*args, **kwargs):
            self.to_background()
            func(*args, **kwargs)
            logger.debug("{}: executed wrapped function: {}".format(self.name, func.__name__))
            if self.in_background.isSet():
                self.to_foreground()
        wrapper.__name__ == func.__name__
        return wrapper

    def process_keymap(self, keymap):
        """
        Processes the keymap, wrapping all callbacks with ``process_callback`` method.
        If a string is passed as callback, replaces it with the corresponding internal method.
        Raises ValueError if callback is not a callable or a name of a callable attribute.
        Raises AttributeError if method name is not found.
        """
        logger.debug("{}: processing keymap - {}".format(self.name, keymap))
        for key, value in keymap.items():
            if isinstance(value, basestring):
                # Using a string means an internal function needs to be used
                # Not wrapping it at the moment
                attribute = getattr(self, value)
                if not callable(attribute): #Wait, is it really a function?
                     raise ValueError("Unknown method string supplied for {}: method {} not found in {}!".format(key, value, self.name or type(self)))
                else:
                    keymap[key] = attribute
            elif callable(value):
                # Callback is an external function
                # Wrapping that in to_background-to_foreground calls
                keymap[key] = self.process_callback(value)
            else:
                raise ValueError("Unknown callback supplied for {}: {}".format(key, type(value)))
        return keymap

    def validate_keymap(self):
        """
        Checks if ``Refresher``'s keymap has all the critical callbacks set. For now,
        the only truly critical callback is ``deactivate`` on "KEY_LEFT".
        If the key already has a callback set, ``validate_keymap`` doesn't replace
        the callback - relying on the developer to do the right decision and
        provide the user with a way to exit the ``Refresher``.
        """
        if not "KEY_LEFT" in self.keymap:
            self.keymap["KEY_LEFT"] = self.deactivate

    def set_keymap(self, keymap):
        """Sets the refresher's keymap (filtered using ``process_keymap`` before setting)."""
        self.keymap = self.process_keymap(keymap)
        self.validate_keymap()

    def update_keymap(self, new_keymap):
        """Updates the refresher's keymap with a replacement keymap (which is also
        filtered using ``process_keymap`` before setting)."""
        processed_keymap = self.process_keymap(new_keymap)
        self.keymap.update(processed_keymap)

    @to_be_foreground
    def activate_keymap(self):
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.set_keymap(self.keymap)
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
