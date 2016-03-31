from evdev import InputDevice as HID, list_devices, ecodes
from time import sleep
import threading
import time


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


class InputDevice():
    """ A driver for HID devices. As for now, supports keyboards and numpads.
    Not yet capable of mapping keys to another keycodes, simply sends the keycodes as they are."""

    stop_flag = False

    def __init__(self, path=None, name=None):
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
        try:
            self.device = HID(self.path)
        except OSError:
            raise
        self.device.grab() #Catch exception if device is already grabbed

    def start(self):
        """Starts listening on the input device. Initialises the IO expander and runs either interrupt-driven or polling loop."""
        self.stop_flag = False
        self.event_loop()

    def stop(self):
        """Sets the ``stop_flag`` for loop functions."""
        self.stop_flag = True

    def event_loop(self):
        """Blocking event loop which just calls supplied callbacks in the keymap."""
        try:
            for event in self.device.read_loop():
                if self.stop_flag:
                    break
                if event.type == ecodes.EV_KEY:
                    key = ecodes.keys[event.code]
                    value = event.value
                    if value == 0:
                        self.send_key(key)
        except IOError as e: 
            if e.errno == 11:
                #raise #Uncomment only if you have nothing better to do 
                pass
        finally:
            self.listening = False

    def send_key(self, key):
        """A hook to be overridden by ``InputListener``. Otherwise, prints out key names as soon as they're pressed so is useful for debugging."""
        print(key)

    def activate(self):
        """Starts a thread with ``start`` function as target."""
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()


if __name__ == "__main__":
    print("Available device names:")
    print([dev.name for dev in get_input_devices()])
    #id = InputDevice(name = "HID 04d9:1603")
    #id.start()
