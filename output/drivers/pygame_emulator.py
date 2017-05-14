"""pygame emulator for lcd screen
allows development of sofware on a without zerophone hardware
e.g. on a laptop with a USB keyboard"""

from time import sleep
from threading import Event
import logging
import pygame_emulator_factory
from luma.core.render import canvas

logger = logging.getLogger(__name__)

class Screen():
    """
    Screen is an important class; all display is done by this class.
    On program start main.py invokes output.py which looks up an output driver and
    the output driver creates a Screen instance.

    Screen provides high-level functions for interaction with display.
    It contains all the high-level logic and
    exposes an interface for system and applications to use.

    menu.py makes callbacks to display_data() and setCursor()
    methods in this class
    """

    cursor_enabled = False
    cursor_pos = (0, 0) #x, y, in characters, not pixels

    def __init__(self, debug=True, **kwargs):
        """ Sets variables for high-level functions.

        Kwargs:

           * ``width`` (default=2): rows of the connected display
           * ``height`` (default=16): columns of the connected display
           * ``debug`` (default=False): debug mode which prints out the commands sent to display
           * ``**kwargs``: all the other arguments
                 get passed to the init_display() function (currently ignored)"""

        logger.debug("entering Screen constructor, kwargs = %s", kwargs)
        self.busy_flag = Event()
        #TODO: this needs to be adjusted based on window/screen size
        self.charwidth = 6
        self.charheight = 8
        self.cols = 128/self.charwidth
        self.rows = 64/self.charheight
        #with the default 128 pixels wide and 64 pixels high screen
        #implicitly required for the splash screen, this works
        #out to be 18 columns wide by 8 rows high
        logger.debug("cols = %d, rows = %d", self.cols, self.rows)
        self.debug = debug
        self.init_display(**kwargs)

    def init_display(self):
        """Creates instance of pygame emulator device and stores it in a member variable. """
        logger.debug("entered pygame_emulator.init_display")
        #note: although the emulator factory allows passing the constructor a width
        #and height, if anything but 128 x 64 is used, it will cause the splash screen
        #to throw an exception.
        self.device = pygame_emulator_factory.get_pygame_emulator_device()
        logger.debug("set device")

    def display_data(self, *args):
        """Displays data on display.
        called from menu.py refresh() so don't remove this method
        This function does the actual work of printing things to display.
        ``*args`` is a list of strings,
                  where each string corresponds to a row of the display,
                  starting with 0.
                  Note:  the emulator does not support passing tuples, lists
                  or anything except comma delimited simple strings as args.
        """
        logger.debug("entered display_data with args = %s.  args type is %s", args, type(args))
        while self.busy_flag.isSet():
            sleep(0.01)
        self.busy_flag.set()
        args = args[:self.rows]
        with canvas(self.device) as draw:
            if self.cursor_enabled:
                dims = (self.cursor_pos[0]-1+2,
                        self.cursor_pos[1]-1,
                        self.cursor_pos[0]+self.charwidth+2,
                        self.cursor_pos[1]+self.charheight+1)
                draw.rectangle(dims, outline="white")
                logger.debug("cursor enabled.  after draw.rectangle with corners: %s", dims)
            else:
                logger.debug("cursor disabled")

            logger.debug("type(args)=%s", type(args))
            for line, arg in enumerate(args):
                logger.debug("line = %s, arg = %s, type(arg)=%s", line, arg, type(arg))
                #Emulator only:  Passing anything except a string to draw.text will cause PIL to
                #throw an exception.  Warn 'em here via the log.
                if not isinstance(arg, basestring):
                    logger.warning(
                        "emulator only likes strings fed to draw.text, prepare for exception")
                y = (line*self.charheight - 1) if line != 0 else 0
                draw.text((2, y), arg, fill="white")
                logger.debug("after draw.text(2,%d), %s", y, arg)

        self.busy_flag.clear()

    def setCursor(self, row, col):
        """
        Called from menu.py refresh() so don't remove this method
        Set current input cursor to ``row`` and ``column`` specified """
        logger.debug("setCursor entered.  row=%d, col=%d", row, col)
        self.cursor_pos = (col*self.charwidth, row*self.charheight)

    def noCursor(self):
        """ Turns the underline cursor off """
        logger.debug("noCursor called")
        self.cursor_enabled = False

    def cursor(self):
        """ Turns the underline cursor on """
        logger.debug("cursor called")
        self.cursor_enabled = True
