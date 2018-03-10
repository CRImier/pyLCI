from __future__ import division

import math
from datetime import datetime, timedelta

from apps import ZeroApp
from ui import Menu, Refresher, Canvas, IntegerAdjustInput
from ui.loading_indicators import CenteredTextRenderer

from helpers import read_or_create_config, local_path_gen

local_path = local_path_gen(__name__)

class ClockApp(ZeroApp, Refresher, CenteredTextRenderer):

    def __init__(self, i, o, *args, **kwargs):
        super(ClockApp, self).__init__(i, o)
        self.menu_name = "Clock"
        self.countdown = None
        self.refresher = Refresher(self.on_refresh, i, o, keymap={"KEY_RIGHT":self.countdown_settings})
        default_config = '{}'
        config_filename = "config.json"
        self.config = read_or_create_config(local_path(config_filename), default_config, self.menu_name+" app")

    def format_countdown(self):
        if not self.countdown: return None
        h, m, s, sign = self.get_countdown_time_left()
        if sign: return None
        return "{}m".format(h*60+m)

    def get_countdown_time_left(self):
        delta = self.countdown["time"]-datetime.now()
        print(delta)
        seconds = delta.seconds
        sign = None
        if delta.days < 0:
            seconds = -seconds
            sign = "+"
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if sign == "+":
            hours = hours+24
        return hours, minutes, seconds, sign

    def countdown_settings(self):
        # Setting an absolute countdown is not yet possible
        # because we don't yet have a TimePicker UI element
        def gmc(): #get menu contents
            countdown_label = self.format_countdown()
            contents = []
            if countdown_label: contents.append(["Countdown: {}".format(countdown_label)])
            #contents.append(["Set absolute", lambda: self.set_countdown(absolute=True)])
            contents.append(["Set relative", self.set_countdown])
            return contents
        Menu([], self.i, self.o, "Countdown settings menu", contents_hook=gmc).activate()

    def set_countdown(self, absolute=False):
        if absolute: raise NotImplementedError # Needs a TimePicker or something like that
        rel_start = 0
        message = "After (in minutes):"
        if self.countdown:
            # A countdown is already active
            # Using it as a starting point
            h, m, s, _ = self.get_countdown_time_left()
            rel_start = h*60+m
        offset = IntegerAdjustInput(rel_start, self.i, self.o, message=message).activate()
        if offset is not None:
            countdown = {"time": datetime.now()+timedelta(minutes=offset)}
            self.countdown = countdown

    def draw_analog_clock(self, c, time, radius="min(*c.size) / 3", clock_x = "center_x+32", clock_y = "center_y+5", h_len = "radius / 2", m_len = "radius - 5", s_len = "radius - 3", **kwargs):
        """Draws the analog clock, with parameters configurable through config.json."""
        center_x, center_y = c.get_center()
        clock_x = eval(clock_x)
        clock_y = eval(clock_y)
        radius = eval(radius)
        c.ellipse((clock_x - radius, clock_y - radius, clock_x + radius, clock_y + radius), fill=False, outline="white")
        self.draw_needle(c, 60 - time.second / 60, eval(s_len), clock_x, clock_y, 1)
        self.draw_needle(c, 60 - time.minute / 60, eval(m_len), clock_x, clock_y, 1)
        self.draw_needle(c, 24 - time.hour / 24, eval(h_len), clock_x, clock_y, 1)

    def draw_countdown(self, c, countdown_x="(center_x/2)-10", countdown_y="center_y/2*3", **kwargs):
        """Draws the digital clock, with parameters configurable through config.json."""
        h, m, s, sign = self.get_countdown_time_left()
        hz, mz, sz = map(lambda x:str(x).zfill(2), (h, m, s))
        string = "{}:{}".format(mz, sz)
        if h: string = hz+":"+string
        if sign: string = sign+string
        center_x, center_y = c.get_center()
        centered_coords = self.get_centered_text_bounds(c, string)
        x = eval(countdown_x)
        y = eval(countdown_y)
        c.text((x, y), string, fill="white")

    def draw_text(self, c, time, text_x="10", text_y="center_y-5", time_format = "%H:%M:%S", **kwargs):
        """Draws the digital clock, with parameters configurable through config.json."""
        time_str = time.strftime(time_format)
        center_x, center_y = c.get_center()
        centered_coords = self.get_centered_text_bounds(c, time_str)
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
        if self.countdown:
            self.draw_countdown(c, **kwargs)
        return c.get_image()

    def draw_needle(self, c, progress, radius, x, y, width):
        # type: (Canvas, float, float, float, float, int) -> None
        hour_angle = math.pi * 2 * progress + math.pi
        c.line(
            (
                int(x),
                int(y),
                int(x + radius * math.sin(hour_angle)),
                int(y + radius * math.cos(hour_angle))
            ),
            width=width,
            fill=True
        )

    def on_start(self):
        super(ClockApp, self).on_start()
        self.refresher.activate()
