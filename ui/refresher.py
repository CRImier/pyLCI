from threading import Event
from time import sleep

import PIL

from helpers import setup_logger
from utils import to_be_foreground
from base_ui import BaseUIElement

logger = setup_logger(__name__, "info")


class RefresherExitException(Exception):
    pass


class Refresher(BaseUIElement):
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
            * ``keymap``: Keymap entries you want to set while Refresher is active. By default, KEY_LEFT deactivates the Refresher, if you wan tto override it, do it carefully.
            * ``name``: Refresher name which can be used internally and for debugging.

        """
        BaseUIElement.__init__(self, i, o, name, input_necessary=False)
        self.set_refresh_interval(refresh_interval)
        self.refresh_function = refresh_function
        self.calculate_intervals()
        self.set_keymap(keymap if keymap else {})
        self.in_foreground = False
        self.in_background = Event()

    @property
    def is_active(self):
        return self.in_background

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
        if not self.in_foreground:
            self.in_foreground = True
            self.activate_input()
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

    @to_be_foreground
    def refresh(self):
        logger.debug("{}: refreshed data on display".format(self.name))
        try:
            data_to_display = self.refresh_function()
        except RefresherExitException:
            logger.info("{}: received exit exception, deactivating".format(self.name))
            self.deactivate()
            return
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
