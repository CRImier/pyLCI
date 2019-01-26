from ui import Menu
from helpers import setup_logger

logger = setup_logger(__name__, "warning")

def get_input_devices():
    """Returns list of all the available InputDevices"""
    from evdev import list_devices
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

    def add_driver(self, path=None, name=None, dtype="hid"):
        if dtype in ["hid"]:
            raise ValueError("Types other than 'hid' are not supported- asked for {}!".format(dtype))
        if dtype == "hid":
            from drivers.hid import InputDevice as HIDDriver
            driver = HIDDriver(path=path, name=name)
            name = "hid"
        self.i.attach_driver(driver, name)
        self.driver_storage[name] = driver
        return name

    def remove_driver(self, name):
        driver = self.driver_storage.pop(name)
        self.i.detach_driver(name)
        driver.atexit()
