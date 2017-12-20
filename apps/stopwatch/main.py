# coding=utf-8

from apps.zero_app import ZeroApp
from ui import Refresher
from ui.utils import Chronometer


class StopwatchApp(ZeroApp):
    def __init__(self, i, o):
        super(StopwatchApp, self).__init__(i, o)
        self.menu_name = "Stopwatch"
        self.counter = Chronometer()
        self.refresher = None
        self.__instructions = ["", "UP/ENTER to start/pause", "RIGHT : restart", "DOWN : reset"]

    def on_start(self):
        super(StopwatchApp, self).on_start()
        self.refresher = Refresher(self.refresh_function, self.i, self.o, .1, {
            "KEY_UP": self.counter.toggle,
            "KEY_RIGHT": self.counter.start,
            "KEY_ENTER": self.counter.toggle,
            "KEY_DOWN": self.counter.stop
        })
        self.refresher.activate()

    def refresh_function(self):
        self.counter.update()
        text_rows = ["{} {}".format(self.get_char(), round(self.counter.elapsed, 2)).center(self.o.cols)]
        text_rows.extend([instruction.center(self.o.cols) for instruction in self.__instructions])
        return text_rows

    def get_char(self):
        return "|>" if self.counter.active else "||"
