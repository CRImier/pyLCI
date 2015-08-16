from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import time
import os
import importlib
from config_parse import read_config
import logging
import Pyro4

def to_be_enabled(func):
    """Decorator for KeyListener class. Is used on functions which require enabled KeyListener to be executed. 
       Currently assumes there has been an error and tries to re-enable the listener."""
    def wrapper(self, *args, **kwargs):
        if not self._enabled:
            if not self._enable():
                return None #TODO: think what's appropriate and what are the times something like that might happen
        else:
            return func(self, *args, **kwargs)
    return wrapper

def comm_fail_possible(func):
    """Decorator for KeyListener class. Is used on functions which require enabled KeyListener to be executed. 
       Currently assumes there has been an error and tries to re-enable the listener."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (Pyro4.errors.CommunicationError, Pyro4.errors.ConnectionClosedError):
            self.comm_error_func()
    return wrapper

class KeyListener():
    """A class which listens for input device events and calls according callbacks if set"""
    _enabled = False
    _listening = False
    keymap = {}
    _callback_object = None
    _stop_flag = False
    _interface = None
    _device = None

    def __init__(self, path=None, name=None, keymap={}):
        """Init function for creating KeyListener object. Checks all the arguments and sets keymap if supplied."""
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
        self.set_keymap(keymap)
        self._enable()

    def _enable(self):
        """Enables listener - sets all the flags and creates devices. Does not start a listening or a listener thread."""
        #TODO: make it re-check path if name was used for the constructor
        #keep in mind that this will get called every time if there's something wrong
        #and input device file nodes aren't strictly mapped to their names
        #__init__ function remake is needed for this
        logging.debug("enabling listener")
        try:
            self._device = InputDevice(self.path)
        except OSError:
            raise
        try:
            self._device.grab() #Catch exception if device is already grabbed
        except IOError:
            pass
        self._enabled = True
        return True

    @to_be_enabled
    def _force_disable(self):
        """Disables listener, is useful when device is unplugged and errors may occur when doing it the right way
           Does not unset flags - assumes that they're already unset."""
        logging.debug("force disabling listener")
        self._stop_listen()
        #Exception possible at this stage if device does not exist anymore
        #Of course, nothing can be done about this =)
        try:
            self._device.ungrab() 
        except IOError:
            pass #Maybe log that device disappeared?
        self._enabled = False

    @to_be_enabled
    def _disable(self):
        """Disables listener - makes it stop listening and ungrabs the device"""
        logging.debug("disabling listener")
        self._stop_listen()
        while self._listening:
            time.sleep(0.01)
        self._device.ungrab()
        self._enabled = False

    def get_available_keys(self):
        """Returns a list of available keys from the device"""
        dict_key = ('EV_KEY', 1L)
        capabilities = self._device.capabilities(verbose=True, absinfo=False)
        keys = [lst[0] for lst in capabilities[dict_key]]
        return keys

    @Pyro4.oneway
    def set_callback(self, key_name, callback):
        """Sets a single callback of the listener"""
        self._keymap[key_name] = callback

    #@Pyro4.oneway
    def set_callback_object(self, object):
        """Sets the object which is the base object of callbacks"""
        self._callback_object = object

    @Pyro4.oneway
    def remove_callback(self, key_name):
        """Sets a single callback of the listener"""
        try:
            self._keymap.remove(key_name)
        except AttributeError:
            pass

    @Pyro4.oneway
    def set_keymap(self, keymap):
        """Sets all the callbacks supplied, removing previously set"""
        self.keymap = keymap

    @Pyro4.oneway
    def replace_keymap_entries(self, keymap):
        """Sets all the callbacks supplied, not removing previously set"""
        for key in keymap.keys:
            set_callback(key, keymap[key])

    @Pyro4.oneway
    def clear_keymap(self):
        """Removes all the callbacks set"""
        self.keymap.clear()

    @to_be_enabled
    @comm_fail_possible
    def _event_loop(self):
        """Blocking event loop which just calls supplied callbacks in the keymap."""
        #TODO: describe callback interpretation ways
        self._listening = True
        try:
            for event in self._device.read_loop():
                if self._stop_flag:
                    break
                if event.type == ecodes.EV_KEY:
                    key = ecodes.keys[event.code]
                    value = event.value
                    if value == 0:
                        logging.debug("processing an event")
                        if key in self.keymap:
                            logging.debug("event has a callback attached, calling it")
                            getattr(self._callback_object, self.keymap[key])()
                        else:
                            print ""
        except KeyError as e:
            self._force_disable()
        except IOError as e: 
            if e.errno == 11:
                #Okay, this error sometimes appears out of blue when I press buttons on a keyboard. Moreover, it's uncaught but due to some logic I don't understand yet the whole thing keeps running. I need to research it.
                logging.debug("That IOError errno=11 again. Need to learn to ignore it somehow.")
        finally:
            self._listening = False

    def _reset(self):
        self._generate_keymap()

    def _signal_interface_addition(self):
        self.stop_listen()
        self.keymap.clear()
        interface_methods = [method for method in dir(self._interface) if callable(getattr(self._interface, method))]
        for method_name in interface_methods:
            setattr(self._interface, method_name, getattr(self, method_name))
        self.set_keymap(self._interface.keymap)
        self.listen()

    def _signal_interface_removal(self):
        self.stop_listen()
        self.keymap.clear()

    @Pyro4.oneway
    @to_be_enabled
    def listen(self):
        """Starts event loop in a thread. Nonblocking."""
        logging.debug("started listening")
        self._stop_flag = False
        self._listener_thread = threading.Thread(target = self._event_loop) 
        self._listener_thread.daemon = True
        self._listener_thread.start()
        return True

    @Pyro4.oneway
    @to_be_enabled
    def stop_listen(self):
        logging.debug("stopped listening")
        self._stop_flag = True
        return True

def get_input_devices():
    """Returns list of all the available InputDevices"""
    return [InputDevice(fn) for fn in list_devices()]

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

if "__name__" != "__main__":
    config = read_config()
    try:
        driver_name = config["input"][0]["driver"]
    except:
        driver_name = None
    if driver_name:
        driver_module = importlib.import_module("input.drivers."+driver_name)
        try:
            driver_args = config["input"][0]["driver_args"]
        except KeyError:
            driver_args = []
        try:
            driver_kwargs = config["input"][0]["driver_kwargs"]
        except KeyError:
            driver_kwargs = {}
        driver = driver_module.InputDevice(*driver_args, **driver_kwargs)
        driver.activate()
    try:
        device_name = config["input"][0]["device_name"]
    except:
        device_name = driver.name
    listener = KeyListener(name=device_name)

