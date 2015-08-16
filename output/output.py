from time import sleep
import threading
from config_parse import read_config
import importlib

#Currently only 16x2 char displays are tested with all the drivers and software, as I simply don't have access to a bigger display yet -_-

class BaseScreen():
    interface = None

    #TODO: make it secure
    def _signal_interface_addition(self):
        self.set_display_func(self.display_data)

    def _signal_interface_removal(self):
        pass

    def expose(self):
        print "Exposing"
        self._pyroDaemon.register(self.display_data) 

    def set_display_func(self, func):
        self._interface.display_data = func

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
