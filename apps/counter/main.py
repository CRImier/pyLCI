# coding=utf-8
from time import time

from input.input import InputListener
from ui import Refresher

INSTRUCTIONS = ["", "UP/ENTER to start/pause", "RIGHT : restart", "DOWN : reset"]

menu_name = "Counter"
total_elapsed_time = None
refresher = None
counter = None
i = None  # Input device
o = None  # Output device


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

    def on_refresh(self):
        if not self.__active: return
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


def get_char(counter):
    return "|>" if counter.active else "||"


def on_refresh_printing():
    global i, o, counter
    counter.on_refresh()
    text_rows = ["{} {}".format(get_char(counter), round(counter.elapsed, 2)).center(o.cols)]
    text_rows.extend([i.center(o.cols) for i in INSTRUCTIONS])
    return text_rows


# run once the app starts
def callback():
    global refresher, counter
    counter = Counter()
    refresher = Refresher(on_refresh_printing, i, o, .1, {
        "KEY_UP": counter.toggle,
        "KEY_RIGHT": counter.start,
        "KEY_ENTER": counter.toggle,
        "KEY_DOWN": counter.stop
    })
    refresher.activate()


def init_app(input, output):
    # type: (InputListener, object) -> None
    global i, o
    i, o = input, output
