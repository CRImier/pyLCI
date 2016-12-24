from evdev import InputDevice as HID, list_devices, ecodes
from time import sleep

from skeleton import InputSkeleton

def get_input_devices():
    """Returns list of all the available InputDevices"""
    return [HID(fn) for fn in list_devices()]

def get_path_by_name(name):
    """Gets HID device path by name, returns None if not found."""
    path = None
    for dev in get_input_devices():
        if dev.name == name:
            path = dev.fn
    return path

def get_name_by_path(path):
    """Gets HID device path by name, returns None if not found."""
    name = None
    for dev in get_input_devices():
        if dev.fn == path:
            name = dev.name
    return name


class InputDevice(InputSkeleton):
    """ A driver for HID devices. As for now, supports keyboards and numpads."""

    def __init__(self, path=None, name=None, **kwargs):
        """Initialises the ``InputDevice`` object.  
                                                                               
        Kwargs:                                                                  
                                                                                 
            * ``path``: path to the input device. If not specified, you need to specify ``name``.
            * ``name``: input device name

        """
        if not name and not path: #No necessary arguments supplied
            raise TypeError("Expected at least path or name; got nothing. =(")
        if not path:
            path = get_path_by_name(name)
        if not name:
            name = get_name_by_path(path)
        if not name and not path: #Seems like nothing was found by get_input_devices
            raise IOError("Device not found")
        self.path = path
        self.name = name
        self.init_hw()
        InputSkeleton.__init__(self, mapping = [], **kwargs)

    def init_hw(self):
        try:
            self.device = HID(self.path)
        except OSError:
            print("Failed HID")
            return False
        else:
            self.device.grab() #Can throw exception if already grabbed
            return True

    def runner(self):
        """Blocking event loop which just calls supplied callbacks in the keymap."""
        try:
            while not self.stop_flag:
                event = self.device.read_one()
                if event is not None and event.type == ecodes.EV_KEY:
                    key = ecodes.keys[event.code]
                    value = event.value
                    if value == 0 and self.enabled:
                        self.send_key(key)
                sleep(0.01)
        except IOError as e: 
            if e.errno == 11:
                #raise #Uncomment only if you have nothing better to do - error seems to appear at random
                pass

    def atexit(self):
        InputSkeleton.atexit(self)
        try:
            self.device.ungrab()
        except:
            pass



if __name__ == "__main__":
    print("Available device names:")
    print([dev.name for dev in get_input_devices()])
    #id = InputDevice(name = get_input_devices()[0].name, threaded=False)
    #id.runner()
