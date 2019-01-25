from ui import Menu
from helpers import setup_logger

from drivers.hid import InputDevice as HIDDriver

from evdev import list_devices

logger = setup_logger(__name__, "warning")

def get_input_devices():
    """Returns list of all the available InputDevices"""
    devices = []
    for fn in list_devices():
        try:
            devices.append(HID(fn))
        except:
            pass

class DeviceManager():
    def __init__(self, i):
        self.i = i
        self.driver_storage = {}

    def get_drivers(self):
        return self.driver_storage

    def add_driver(self, path=None, name=None, type="hid"):
        if type != "hid":
            raise ValueError("Types other than 'hid' are not supported- asked for {}!".format(type))
        driver = HIDDriver(path=path, name=name)
        name = "hid"
        self.i.attach_driver(driver, name)
        self.driver_storage[name] = driver
        return name

    def remove_driver(self, name):
        driver = self.driver_storage.pop(name)
        self.i.detach_driver(name)
        driver.atexit()
