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
