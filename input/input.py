import threading
import importlib
import atexit
from time import sleep
import Queue
from helpers.config_parse import read_config



listener = None
driver = None

class InputListener():
    """A class which listens for input device events and calls according callbacks if set"""
    listening = False
    keymap = {}
    stop_flag = False

    def __init__(self, driver, keymap={}):
        """Init function for creating KeyListener object. Checks all the arguments and sets keymap if supplied."""
        self.driver = driver
        self.queue = Queue.Queue()
        self.driver.send_key = self.receive_key #Overriding the send_key method so that keycodes get sent to InputListener
        self.set_keymap(keymap)

    def receive_key(self, key):
        try:
            self.queue.put(key)
        except:
            raise #Just collecting possible exceptions for now

    def set_callback(self, key_name, callback):
        """Sets a single callback of the listener"""
        self.keymap[key_name] = callback

    def remove_callback(self, key_name):
        """Sets a single callback of the listener"""
        self.keymap.remove(key_name)

    def set_keymap(self, keymap):
        """Sets all the callbacks supplied, removing previously set"""
        self.keymap = keymap

    def replace_keymap_entries(self, keymap):
        """Sets all the callbacks supplied, not removing previously set but overwriting those with same keycodes"""
        for key in keymap.keys:
            set_callback(key, keymap[key])

    def clear_keymap(self):
        """Removes all the callbacks set"""
        self.keymap.clear()

    def event_loop(self):
        """Blocking event loop which just calls supplied callbacks in the keymap."""
        self.listening = True
        try:
            while not self.stop_flag:
                try:
                    key = self.queue.get(False, 0.1)
                except Queue.Empty:
                    sleep(0.05)
                except AttributeError:
                    print("Heh, caught that.")
                else:
                    if key in self.keymap:
                        callback = self.keymap[key]
                        callback()
        except:
            raise
        finally:
            self.listening = False

    def listen(self):
        """Start  event_loop in a thread. Nonblocking."""
        self.stop_flag = False
        self.driver.activate()
        self.listener_thread = threading.Thread(target = self.event_loop) 
        self.listener_thread.daemon = False
        self.listener_thread.start()
        return True

    def stop_listen(self):
        self.stop_flag = True
        self.driver.stop()
        return True


def init():
    global listener, driver
    config = read_config()
    input_config = config["input"][0]
    driver_name = input_config["driver"]
    driver_module = importlib.import_module("input.drivers."+driver_name)
    args = input_config["args"] if "args" in input_config else []
    kwargs = input_config["kwargs"] if "kwargs" in input_config else {}
    driver = driver_module.InputDevice(*args, **kwargs)
    listener = InputListener(driver)
    atexit.register(listener.stop_listen)
