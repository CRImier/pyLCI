#!/usr/bin/python

#draw.rectangle((0, 0, device.width-1, device.height-2), outline="white", fill="black")

# based on code from Adafruit, lrvick and LiquidCrystal
# lrvick - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
# Adafruit - https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
# SSD1306 library - ################

from time import sleep
from oled.serial import spi
from oled.device import ssd1306, sh1106, ssd1331
from oled.render import canvas
from time import sleep
from threading import Event
from backlight import *

def delayMicroseconds(microseconds):
    seconds = microseconds / float(1000000)  # divide microseconds by 1 million for seconds
    sleep(seconds)

def delay(milliseconds):
    seconds = milliseconds / float(1000)  # divide microseconds by 1 million for seconds
    sleep(seconds)


class Screen(BacklightManager):
    """An object that provides high-level functions for interaction with display. It contains all the high-level logic and exposes an interface for system and applications to use."""

    #buffer = " "
    #redraw_coefficient = 0.5

    type = ["char"] 

    def __init__(self, debug = False, buffering = True, **kwargs):
        """ Sets variables for high-level functions.
        
        Kwargs:

           * ``width`` (default=2): rows of the connected display
           * ``height`` (default=16): columns of the connected display
           * ``debug`` (default=False): debug mode which prints out the commands sent to display
           * ``**kwargs``: all the other arguments, get passed further to HD44780.init_display() function"""
        self.serial = spi(device=0, port=0, bcm_DC=6, bcm_RST=5)
        self.busy_flag = Event()
        self.charwidth = 5
        self.charheight = 8
        self.cols = 104/self.charwidth
        self.rows = 64/self.charheight
        self.debug = debug
        #self.buffering = buffering
        #self.buffer = [" "*self.cols for i in range(self.rows)]
        self.init_display(**kwargs)
        BacklightManager.init_backlight(self, **kwargs)
        self.cursor_pos = (0, 0)

    @enable_backlight_wrapper
    def enable_backlight(self):
        self.device.show()

    @disable_backlight_wrapper
    def disable_backlight(self):
        self.device.hide()

    def init_display(self, autoscroll=False, **kwargs):
        """Initializes HD44780 controller. """
        self.device = sh1106(self.serial, width=128, height=64)

    def _display_data(self, *args):
        """Displays data on display. This function checks if the display contents can be redrawn faster by buffering them and checking the output, then either changes characters one-by-one or redraws the screen completely.
        
        ``*args`` is a list of strings, where each string corresponds to a row of the display, starting with 0."""
        #Formatting the args list to simplify the processing
        args = list(args[:self.rows]) #Cut it to our max length and convert to list so we can change it
        for i, string in enumerate(args): #Pad each string
            args[i] = string[:self.cols].ljust(self.cols)
        if len(args) < self.rows: #Pad with empty strings if it's not yet padded
            for i in range(self.rows-len(args)): 
                args.append(" "*self.cols)
        diffs = [[] for i in range(self.rows)]
        for i, string in enumerate(args):
            for j, char in enumerate(string):
                if self.buffer[i][j] != char:
                    diffs[i].append(j)
        if float(sum([len(diff) for diff in diffs]))/(self.rows*self.cols) > self.redraw_coefficient:
            self._display_data(*args) #Redrawing the display
            self.buffer = args
        else:
            for row_num, row_diffs in enumerate(diffs):
                for i, char_cpos in enumerate(row_diffs):
                    self.setCursor(row_num, char_cpos)
                    self.write_byte(ord(args[row_num][char_cpos]), char_mode=True)
            self.buffer = args

    @activate_backlight_wrapper
    def display_data(self, *args):
        """Displays data on display. This function does the actual work of printing things to display.
        
        ``*args`` is a list of strings, where each string corresponds to a row of the display, starting with 0."""
        while self.busy_flag.isSet():
            sleep(0.01)
        self.busy_flag.set()
        self.clear()
        args = args[:self.rows]
        with canvas(self.device) as draw:
            for line, arg in enumerate(args):
                self.setCursor(line, 0)
                x = 0*self.charwidth
                y = line*self.charheight - 1 if line != 0 else 0
                draw.text((x, y), arg, fill="white")
        self.busy_flag.clear()

    def println(self, line):
        """Prints a line on the screen (assumes position is set as intended)"""
        x = self.cursor_pos[1]*self.charwidth
        y = self.cursor_pos[0]*self.charheight
        with canvas(self.device) as draw:
            draw.text((x, y), line, fill="white")

    def home(self):
        """Returns cursor to home position. If the display is being scrolled, reverts scrolled data to initial position.."""
        self.setCursor(0, 0)

    def clear(self):
        """Clears the display."""
        pass

    def setCursor(self, row, col):
        """ Set current input cursor to ``row`` and ``column`` specified """
        self.cursor_pos = (row, col)

    def createChar(self, char_num, char_contents):
        """Stores a character in the LCD memory so that it can be used later.
        char_num has to be between 0 and 7 (including)
        char_contents is a list of 8 bytes (only 5 LSBs are used)"""
        pass

    def noDisplay(self):
        """ Turn the display off (quickly) """
        pass

    def display(self):
        """ Turn the display on (quickly) """
        pass

    def noCursor(self):
        """ Turns the underline cursor off """
        pass

    def cursor(self):
        """ Turns the underline cursor on """
        pass

    def noBlink(self):
        """ Turn the blinking cursor off """
        pass
	
    def blink(self):
        """ Turn the blinking cursor on """
        pass

    def scrollDisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
        pass

    def scrollDisplayRight(self):
        """ These commands scroll the display without changing the RAM """
        pass

    def leftToRight(self):
        """ This is for text that flows Left to Right """
        pass

    def rightToLeft(self):
        """ This is for text that flows Right to Left """
        pass

    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
        pass

    def noAutoscroll(self):
        """ This will 'left justify' text from the cursor """
        pass
