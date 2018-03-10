from __future__ import division

import math
from datetime import datetime

from apps import ZeroApp
from ui import Refresher, Canvas
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

    def draw_analog_clock(self, c, time, radius="min(*c.size) / 3", clock_x = "center_x+32", clock_y = "center_y+5", h_len = "radius / 2", m_len = "radius - 5", s_len = "radius - 3", **kwargs):
        """Draws the analog clock, with parameters configurable through config.txt."""
        center_x, center_y = c.get_center()
        clock_x = eval(clock_x)
        clock_y = eval(clock_y)
        radius = eval(radius)
        c.ellipse((clock_x - radius, clock_y - radius, clock_x + radius, clock_y + radius), fill=False, outline="white")
        self.draw_needle(c, 60 - time.second / 60, eval(s_len), clock_x, clock_y, 1)
        self.draw_needle(c, 60 - time.minute / 60, eval(m_len), clock_x, clock_y, 1)
        self.draw_needle(c, 24 - time.hour / 24, eval(h_len), clock_x, clock_y, 1)

    def draw_text(self, c, time, text_x="10", text_y="center_y-5", time_format = "%H:%M:%S", **kwargs):
        """Draws the digital clock, with parameters configurable through config.json."""
        time_str = time.strftime(time_format)
        center_x, center_y = c.get_center()
        bounds = self.get_centered_text_bounds(c, time_str)
        x = eval(text_x)
        y = eval(text_y)
        c.text(time_str, (x, y))

    def on_refresh(self):
        current_time = datetime.now()
        return self.render_clock(current_time, **self.config)

    def render_clock(self, time, **kwargs):
        c = Canvas(self.o)
        width, height = c.size
        self.draw_text(c, time, **kwargs)
        self.draw_analog_clock(c, time, **kwargs)
        return c.get_image()

    def draw_needle(self, c, progress, radius, x, y, width):
        # type: (Canvas, float, float, float, float, int) -> None
        hour_angle = math.pi * 2 * progress + math.pi
        c.line(
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
