from __future__ import division

import math
from datetime import datetime

from luma.core.render import canvas

from apps import ZeroApp
from ui import Refresher
from ui.loading_indicators import CenteredTextRenderer

from helpers import read_or_create_config, local_path_gen

local_path = local_path_gen(__name__)

class ClockApp(ZeroApp, Refresher, CenteredTextRenderer):

    def __init__(self, i, o, *args, **kwargs):
        super(ClockApp, self).__init__(i, o)
        self.menu_name = "Clock"
        self.refresher = Refresher(self.on_refresh, i, o)
        default_config = '{}'
        config_filename = "config.json"
        self.config = read_or_create_config(local_path(config_filename), default_config, self.menu_name+" app")

    def draw_analog_clock(self, draw, time, radius="min(*self.o.device.size) / 3", clock_x = "center_x+32", clock_y = "center_y+5", h_len = "radius / 2", m_len = "radius - 5", s_len = "radius - 3", **kwargs):
        """Draws the analog clock, with parameters configurable through config.txt."""
        center_x, center_y = self.get_center(self.o.device.size)
        clock_x = eval(clock_x)
        clock_y = eval(clock_y)
        radius = eval(radius)
        draw.ellipse((clock_x - radius, clock_y - radius, clock_x + radius, clock_y + radius), fill=False, outline="white")
        self.draw_needle(draw, 60 - time.second / 60, eval(s_len), clock_x, clock_y, 1)
        self.draw_needle(draw, 60 - time.minute / 60, eval(m_len), clock_x, clock_y, 1)
        self.draw_needle(draw, 24 - time.hour / 24, eval(h_len), clock_x, clock_y, 1)

    def draw_text(self, draw, time, text_x="10", text_y="center_y-5", time_format = "%H:%M:%S", **kwargs):
        """Draws the digital clock, with parameters configurable through config.txt."""
        time_str = time.strftime(time_format)
        center_x, center_y = self.get_center(self.o.device.size)
        bounds = self.get_centered_text_bounds(draw, time_str, self.o.device.size)
        x = eval(text_x)
        y = eval(text_y)
        draw.text((x, y), time_str, fill="white")

    def on_refresh(self):
        current_time = datetime.now()
        return self.render_clock(current_time, **self.config)

    def render_clock(self, time, **kwargs):
        c = canvas(self.o.device)
        c.__enter__()
        width, height = c.device.size
        draw = c.draw
        self.draw_text(draw, time, **kwargs)
        self.draw_analog_clock(draw, time, **kwargs)
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
