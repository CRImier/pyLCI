#!/usr/bin/python

from luma_driver import LumaScreen
from luma.oled.device import ssd1306

class Screen(LumaScreen):
    """An object that provides high-level functions for interaction with display. It contains all the high-level logic and exposes an interface for system and applications to use."""

    def init_display(self, autoscroll=False, **kwargs):
        """Initializes SH1106 controller. """
        self.device = ssd1306(self.serial, width=128, height=64)
