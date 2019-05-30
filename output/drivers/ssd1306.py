#!/usr/bin/python

from luma_driver import LumaScreen
from luma.oled.device import ssd1306

from output.output import OutputDevice


class Screen(LumaScreen, OutputDevice):
    """An object that provides high-level functions for interaction with display. It contains all the high-level logic and exposes an interface for system and applications to use."""

    default_rotate = 0

    def init_display(self, **kwargs):
        """Initializes SSD1306 controller. """
        self.rotate = kwargs.pop("rotate", self.default_rotate)
        self.device = ssd1306(self.serial, width=self.width, height=self.height, rotate=self.rotate)
