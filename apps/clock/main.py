from __future__ import division

import math
from datetime import datetime

from luma.core.render import canvas

from apps import ZeroApp
from ui import Refresher
from ui.loading_indicators import CenteredTextRenderer


class ClockApp(ZeroApp, Refresher, CenteredTextRenderer):

    def __init__(self, i, o, *args, **kwargs):
        super(ClockApp, self).__init__(i, o)
        self.menu_name = "Clock"
        self.refresher = Refresher(self.on_refresh, i, o)

    def on_refresh(self):
        now = datetime.now()
        c = canvas(self.o.device)
        c.__enter__()
        x, y = c.device.size
        radius = min(x, y) / 4
        x, y = self.get_center(self.o.device.size)
        draw = c.draw
        time_str = now.strftime("%H:%M:%S")
        bounds = self.get_centered_text_bounds(draw, time_str, self.o.device.size)
        draw.text((bounds.left, 0), time_str, fill="white")

        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=False, outline="white")
        self.draw_needle(draw, 60 - now.second / 60, radius, x, y, 1)
        self.draw_needle(draw, 60 - now.minute / 60, radius, x, y, 1)
        self.draw_needle(draw, 24 - now.hour / 24, radius / 2, x, y, 1)

        return c.image

    def draw_needle(self, draw, progress, radius, x, y, width):
        # type: (ImageDraw, float, float, float, float, int) -> None
        hour_angle = math.pi * 2 * progress + math.pi
        draw.line(
            (
                x,
                y,
                x + radius * math.sin(hour_angle),
                y + radius * math.cos(hour_angle)
            ),
            width=width,
            fill=True
        )

    def on_start(self):
        super(ClockApp, self).on_start()
        self.refresher.activate()

# def show_time():
#     now = datetime.now()
#     return [now.strftime("%H:%M:%S").center(o.cols), now.strftime("%Y-%m-%d").center(o.cols)]

# i = None; o = None
#
# def callback():
#     Refresher(show_time, i, o, 1, name="Clock refresher").activate()
#
# def init_app(input, output):
#     global i, o
#     i = input; o = output #Getting references to output and input device objects and saving them as globals
#
