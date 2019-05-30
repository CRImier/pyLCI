from functools import wraps

KEY_PRESSED = 1
KEY_RELEASED = 0
KEY_HELD = 2

def cb_needs_key_state(callback, new_function=False):
    if new_function:
        @wraps(callback)
        def func(*args, **kwargs):
            return callback(*args, **kwargs)
        func.zpui_icb_pass_key_state = True
        return func
    # Creating a new function not requested, just modify in-place
    if hasattr(callback, "__func__"):
        callback.__func__.zpui_icb_pass_key_state = True
    else:
        callback.zpui_icb_pass_key_state = True
    return callback
