#!/usr/bin/python

#draw.rectangle((0, 0, device.width-1, device.height-2), outline="white", fill="black")

# based on code from Adafruit, lrvick and LiquidCrystal
# lrvick - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
# Adafruit - https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
# SSD1306 library - ################

from time import sleep
from luma.core.serial import spi, i2c
from luma.core.render import canvas
from time import sleep
from threading import Event
from backlight import *

def delayMicroseconds(microseconds):
    seconds = microseconds / float(1000000)  # divide microseconds by 1 million for seconds
    sleep(seconds)

def delay(milliseconds):
    seconds = milliseconds / float(1000)  # divide microseconds by 1 million for seconds
    sleep(seconds)


class LumaScreen(BacklightManager):
    """An object that provides high-level functions for interaction with display. It contains all the high-level logic and exposes an interface for system and applications to use."""

    #buffer = " "
    #redraw_coefficient = 0.5
    current_image = None

    type = ["char", "b&w-pixel"] 
    cursor_enabled = False
    cursor_pos = (0, 0) #x, y

    def __init__(self, hw = "spi", port=None, address = 0, debug = False, buffering = True, **kwargs):
        if hw == "spi":
            if port is None: port = 0
            self.serial = spi(port=port, device=address, bcm_DC=6, bcm_RST=5)
        elif hw == "i2c":
            if port is None: port = 1
            if isinstance(address, basestring): address = int(address, 16)
            self.serial = i2c(port=port, address=address)
        else:
            raise ValueError("Unknown interface type: {}".format(hw))
        self.address = address
        self.busy_flag = Event()
        self.width = 128
        self.height = 64
        self.charwidth = 6
        self.charheight = 8
        self.cols = self.width/self.charwidth
        self.rows = self.height/self.charheight
        self.debug = debug
        #self.buffering = buffering
        #self.buffer = [" "*self.cols for i in range(self.rows)]
        self.init_display(**kwargs)
        BacklightManager.init_backlight(self, **kwargs)

    @enable_backlight_wrapper
    def enable_backlight(self):
        self.device.show()

    @disable_backlight_wrapper
    def disable_backlight(self):
        self.device.hide()

    @activate_backlight_wrapper
    def display_image(self, image):
        if self.current_image:
            del self.current_image #Freeing memory
        self.device.display(image)    
        self.current_image = image

    def display_data(self, *args):
        """Displays data on display. This function does the actual work of printing things to display.
        
        ``*args`` is a list of strings, where each string corresponds to a row of the display, starting with 0."""
        while self.busy_flag.isSet():
            sleep(0.01)
        self.busy_flag.set()
        args = args[:self.rows]
        with canvas(self.device) as draw:
            if self.cursor_enabled:
                dims = (self.cursor_pos[0]-1+2, self.cursor_pos[1]-1, self.cursor_pos[0]+self.charwidth+2, self.cursor_pos[1]+self.charheight+1)
                draw.rectangle(dims, outline="white")
            for line, arg in enumerate(args):
                y = (line*self.charheight - 1) if line != 0 else 0
                draw.text((2, y), arg, fill="white")
        self.busy_flag.clear()

    def home(self):
        """Returns cursor to home position. If the display is being scrolled, reverts scrolled data to initial position.."""
        self.setCursor(0, 0)

    def clear(self):
        """Clears the display."""
        pass

    def setCursor(self, row, col):
        """ Set current input cursor to ``row`` and ``column`` specified """
        self.cursor_pos = (col*self.charwidth, row*self.charheight)

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
        self.cursor_enabled = False

    def cursor(self):
        """ Turns the underline cursor on """
        self.cursor_enabled = True

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
