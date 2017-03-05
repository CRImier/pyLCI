import importlib

screen = None

def init(output_config):
    """ This function is called by main.py to read the output configuration, pick the corresponding drivers and initialize a Screen object.

    It also sets ``screen`` global of ``output`` module with created ``Screen`` object."""
    global screen
    #Currently only the first screen in the config is initialized
    screen_config = output_config[0]
    driver_name = screen_config["driver"]
    driver_module = importlib.import_module("output.drivers."+driver_name)
    args = output_config["args"] if "args" in screen_config else []
    kwargs = output_config["kwargs"] if "kwargs" in screen_config else {}
    screen = driver_module.Screen(*args, **kwargs)
