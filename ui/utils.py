import logging
from functools import wraps

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def to_be_foreground(func):
    # A safety check wrapper so that certain functions can't possibly be called
    # if UI element is not the one active
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
    # A safety check wrapper so that there's no race conditions between functions able to change position/value
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert self.value_lock, "Class has no member self.value_lock"  # todo:maybe we should create it here ?
        # Value-changing code likely to run in concurrent thread and therefore we need a lock
        if self.__locked_name__ is not None:
            logger.warning(
                "Another function already locked the thread! Name is {}, current is {}".format(
                    self.__locked_name__,
                    func.__name__
                )
            )
        self.value_lock.acquire()
        self.__locked_name__ = func.__name__
        logger.debug("Locked function {}".format(func.__name__))
        result = func(self, *args, **kwargs)
        self.value_lock.release()
        logger.debug("Unlocked function {}".format(func.__name__))
        self.__locked_name__ = None
        return result

    return wrapper
