#!/usr/bin/python

#
# based on code from Adafruit, lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
# Adafruit - https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
#

from time import sleep

def delayMicroseconds(microseconds):
    seconds = microseconds / float(1000000)  # divide microseconds by 1 million for seconds
    sleep(seconds)

import RPi.GPIO as GPIO

from hd44780 import HD44780

class Screen(HD44780):

    def __init__(self, **kwargs):
        """ Initializes the GPIO-driven HD44780 display
        
        Kwargs:
           * ``pins``: list of GPIO pins for driving display data bits: [DB4, DB5, DB6, DB7]"""
        self.debug = kwargs.pop("debug", False)
        self.rs_pin=kwargs.pop("rs_pin")
        self.en_pin=kwargs.pop("en_pin")
        self.pins=kwargs.pop("pins")
        rows = kwargs.pop("rows", 2)
        cols = kwargs.pop("cols", 16)
        HD44780.__init__(self, rows = rows, cols = cols, debug = self.debug)
        GPIO.setmode(GPIO.BCM)
        if not self.debug:
            GPIO.setwarnings(False)
        GPIO.setup(self.en_pin, GPIO.OUT)
        GPIO.setup(self.rs_pin, GPIO.OUT)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        self.init_display(**kwargs)
        
    def write_byte(self, byte, char_mode=False):
        if self.debug and not char_mode:        
            print(hex(byte))                    
        self.write4bits(byte >> 4, char_mode)   
        self.write4bits(byte & 0x0F, char_mode) 

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """
        bits = bin(bits)[2:][-4:].zfill(4)
        GPIO.output(self.rs_pin, char_mode)
        for index, bit in enumerate(bits[::-1]):
            GPIO.output(self.pins[index], int(bit))
        GPIO.output(self.en_pin, False)
        delayMicroseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns
        GPIO.output(self.en_pin, True)
        delayMicroseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns
        GPIO.output(self.en_pin, False)
        delayMicroseconds(1)       # commands need > 37us to settle


if __name__ == "__main__":
    screen = Screen(pins=[25, 24, 23, 18], rs_pin = 22, en_pin=27)
    line = "0123456789012345"
    if True:
        screen.display_data(line, line[::-1])
        sleep(1)
        screen.display_data(line[::-1], line)
        sleep(1)
        screen.clear()
