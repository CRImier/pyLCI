import threading
import importlib
import atexit
from time import sleep
import Queue
from helpers import read_config

listener = None

class InputListener():
    """A class which listens for input device events and calls according callbacks if set"""
    listening = False
    keymap = {}
    stop_flag = False

    def __init__(self, drivers, keymap={}):
        """Init function for creating KeyListener object. Checks all the arguments and sets keymap if supplied."""
        self.drivers = drivers
        self.queue = Queue.Queue()
        for driver, _ in self.drivers:
            driver.send_key = self.receive_key #Overriding the send_key method so that keycodes get sent to InputListener
        self.set_keymap(keymap)

    def receive_key(self, key):
        """ This is the method that receives keypresses from drivers and puts them into ``self.queue`` for ``self.event_loop`` to receive """
        try:
            self.queue.put(key)
        except:
            raise #Just collecting possible exceptions for now

    def set_callback(self, key_name, callback):
        """Sets a single callback of the listener"""
        self.keymap[key_name] = callback

    def remove_callback(self, key_name):
        """Removes a single callback of the listener"""
        self.keymap.remove(key_name)

    def set_keymap(self, keymap):
        """Sets all the callbacks supplied, removing the previously set keymap completely"""
        self.keymap = keymap

    def replace_keymap_entries(self, keymap):
        """Sets all the callbacks supplied, not removing previously set but overwriting those with same keycodes"""
        for key in keymap.keys:
            set_callback(key, keymap[key])

    def clear_keymap(self):
        """Removes all the callbacks set"""
        self.keymap = {}

    def event_loop(self):
        """Blocking event loop which just calls callbacks in the keymap once corresponding keys are received in the ``self.queue``."""
        self.listening = True
        try:
            while not self.stop_flag:
                try:
                    key = self.queue.get(False, 0.1)
                except Queue.Empty:
                    sleep(0.1)
                except AttributeError:
                    print("Heh, caught that.") #Typically gets printed if InputListener exits abnormally upon program termination
                else:
                    self.process_key(key)
        except:
            raise
        finally:
            self.listening = False

    def process_key(self, key):
        if key in self.keymap:
            callback = self.keymap[key]
            try:
                callback()
            except Exception as e:
                self.handle_callback_exception(key, callback, e)
            finally:
                return
        
    def handle_callback_exception(self, key, callback, e):
        print("Exception caused by callback {} when key {} was received".format(callback, key))
        print("Exception: {}".format(e))
        #raise e
        import pdb;pdb.set_trace()

    def listen(self):
        """Start  event_loop in a thread. Nonblocking."""
        self.stop_flag = False
        for driver, _ in self.drivers:
            driver.start()
        self.listener_thread = threading.Thread(target = self.event_loop) 
        self.listener_thread.daemon = False
        self.listener_thread.start()
        return True

    def stop_listen(self):
        """This sets a flag for ``event_loop`` to stop. It also calls a ``stop`` method of the input driver ``InputListener`` is using."""
        self.stop_flag = True
        for driver, _ in self.drivers:
            driver.stop()
        return True

    def atexit(self):
        """Exits driver (if necessary) if something wrong happened or pyLCI exits. Also, stops the listener"""
        self.stop_listen()
        for driver, _ in self.drivers:
            if hasattr(driver, "atexit"):
                driver.atexit()
        try:
            self.listener_thread.join()
        except AttributeError:
            pass
        


def init():
    """ This function is called by main.py to read the input configuration, pick the corresponding drivers and initialize InputListener.
 
    It also sets ``listener`` globals of ``input`` module with driver and listener respectively, as well as registers ``listener.stop()`` function to be called when script exits since it's in a blocking non-daemon thread."""
    global listener
    config = read_config("config.json")
    input_configs = config["input"]
    drivers = []
    for input_config in input_configs:
        driver_name = input_config["driver"]
        driver_module = importlib.import_module("input.drivers."+driver_name)
        args = input_config["args"] if "args" in input_config else []
        kwargs = input_config["kwargs"] if "kwargs" in input_config else {}
        driver = driver_module.InputDevice(*args, **kwargs)
        drivers.append([driver, driver_name])
    listener = InputListener(drivers)
    atexit.register(listener.atexit)
