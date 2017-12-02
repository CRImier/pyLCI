from functools import wraps


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


def check_value_lock(func):
    # A safety check wrapper so that there's no race conditions between functions able to change position/value
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert self.value_lock, "Class has no member self.value_lock"  # todo:maybe we should create it here ?
        # Value-changing code likely to run in concurrent thread and therefore we need a lock
        # if self.__locked_name__ is not None: print("Another function already locked the thread! Name is {}, current is {}".format(self.__locked_name__, func.__name__))
        self.value_lock.acquire()
        # self.__locked_name__ = func.__name__
        # print("Locked function {}".format(func.__name__))
        result = func(self, *args, **kwargs)
        self.value_lock.release()
        # print("Unlocked function {}".format(func.__name__))
        # self.__locked_name__ = None
        return result

    return wrapper
