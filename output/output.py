from time import sleep
import threading
from config_parse import read_config
import importlib

#Currently only 16x2 char displays are tested with all the drivers and software, as I simply don't have access to a bigger display yet -_-

def _wrap(func, interface):
    def wrapper(*args, **kwargs):
        interface.displayed_data = args
        print args
        return func(*args, **kwargs)
    return wrapper


class BaseScreen():
    interface = None

    #TODO: make it secure
    def _signal_interface_addition(self):
        self._interface.display_data = _wrap(self.display_data, self._interface)
        self.display_data(*self._interface.displayed_data)

    def _signal_interface_removal(self):
        pass


if "__name__" != "__main__":
    config = read_config()
    driver_name = config["output"][0]["driver"]
    driver_module = importlib.import_module("output.drivers."+driver_name)
    try:
        driver_args = config["output"][0]["driver_args"]
    except KeyError:
        driver_args = []
    try:
        driver_kwargs = config["output"][0]["driver_kwargs"]
    except KeyError:
        driver_kwargs = {}
    screen = driver_module.Screen(*driver_args, **driver_kwargs)
