import logging
from functools import wraps
from time import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def to_be_foreground(func):
    """ A safety check wrapper so that certain functions can't possibly be called
    if UI element is not the one active"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False

    return wrapper


def clamp(value, _min, _max):
    return max(_min, min(value, _max))


def clamp_list_index(value, _list):
    return clamp(value, 0, len(_list) - 1)


def check_value_lock(func):
    """ A safety check wrapper so that there's no race conditions
    between functions that are able to change position/value"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert self.value_lock, "Class has no member self.value_lock"  # todo:maybe we should create it here ?
        # Value-changing code is likely to run in concurrent thread and therefore we need a lock
        if self.__locked_name__ is not None:
            logger.warning(
                "Another function already working with the value! Name is {}, current is {}".format(
                    self.__locked_name__,
                    func.__name__
                )
            )
        with self.value_lock:
            self.__locked_name__ = func.__name__
            logger.debug("Locked function {}".format(func.__name__))
            result = func(self, *args, **kwargs)
        logger.debug("Unlocked function {}".format(func.__name__))
        self.__locked_name__ = None
        return result

    return wrapper


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

    def restart(self):
        self.start()


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
