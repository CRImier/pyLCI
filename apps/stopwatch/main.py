# coding=utf-8
from time import time

from apps.zero_app import ZeroApp
from ui import Refresher


class Chronometer(object):
    def __init__(self):
        self.__active = False
        self.__last_call = time()

    def tick(self):
        """
        :rtype: int
        :return: the time elapsed since the previous tick
        """
        now = time()
        elapsed = now - self.__last_call
        self.__last_call = now
        return elapsed


class Counter(object):
    def __init__(self):
        self.__active = False
        self.__cron = Chronometer()
        self.__elapsed = 0

    @property
    def active(self):
        return self.__active

    @property
    def elapsed(self):
        return self.__elapsed

    def update(self):
        if not self.__active:
            return
        self.__elapsed += self.__cron.tick()

    def stop(self):
        self.__cron.tick()
        self.__elapsed = 0
        self.__active = False

    def pause(self):
        self.__active = False

    def resume(self):
        self.__cron.tick()
        self.__active = True

    def start(self):
        self.stop()
        self.resume()

    def toggle(self):
        self.pause() if self.active else self.resume()


class StopwatchApp(ZeroApp):
    def __init__(self, i, o):
        super(StopwatchApp, self).__init__(i, o)
        self.menu_name = "Stopwatch"
        self.counter = Counter()
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
