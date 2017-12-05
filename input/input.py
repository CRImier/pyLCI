from threading import Thread, Event
from traceback import print_exc
from time import sleep
import importlib
import atexit
import Queue
import sys

class CallbackException(Exception):
    def __init__(self, errno=0, message=""):
        self.errno = errno
        self.message = message

class InputProcessor():
    """A class which listens for input device events and passes them to InputProxy
    instance of the currently active context."""
    stop_flag = None
    thread_index = 0
    backlight_cb = None

    def __init__(self, drivers):
        self.drivers = drivers
        self.queue = Queue.Queue()
        for driver in self.drivers.values():
            driver.send_key = self.receive_key #Overriding the send_key method so that keycodes get sent to InputListener

    def receive_key(self, key):
        """ This is the method that receives keypresses from drivers and puts
        them into ``self.queue``, to be processed by ``self.event_loop``"""
        try:
            self.queue.put(key)
        except:
            #TODO: add logger
            raise #Just collecting possible exceptions for now

    def event_loop(self, index):
        """Blocking event loop which just calls callbacks in the keymap
        once corresponding keys are received in the ``self.queue``."""
        #TODO: use a logger
        #print("Starting event loop "+str(index))
        self.stop_flag = Event()
        stop_flag = self.stop_flag #Saving a reference.
        #stop_flag is an object that will signal the current input thread to exit or not exit once it's done processing a callback.
        #It'll be called just before self.stop_flag will be overwritten. However, we've got a reference to it and now can check the exact object this thread itself constructed.
        #Praise the holy garbage collector.
        stop_flag.clear()
        while not stop_flag.isSet():
            try:
                key = self.queue.get(False, 0.1)
            except Queue.Empty:
                sleep(0.1)
            except AttributeError:
                pass #Typically happens if InputListener exits abnormally upon program termination
            else:
                self.process_key(key)
        #TODO: use a logger
        #print("Stopping event loop "+str(index))

    def process_key(self, key):
        #Nonmaskable callbacks are supposed to work even when the screen backlight is off
        #(since, right now, they're actions like "volume up/down" and "next song")
        if key in self.nonmaskable_keymap:
            callback = self.nonmaskable_keymap[key]
            self.handle_callback(callback, key)
            return
        #Checking backlight state, turning it on if necessary
        if callable(self.backlight_cb):
            try:
                backlight_was_off = self.backlight_cb()
            except:
                print("Exception while calling the backlight check callback!")
                print_exc()
            else:
                #If backlight was off, ignore the keypress
                if backlight_was_off is True:
                    return
        #Now, all the other options:
        #Simple callbacks
        if key in self.keymap:
            callback = self.keymap[key]
            self.handle_callback(callback, key)
        #Maskable callbacks
        elif key in self.maskable_keymap:
            callback = self.maskable_keymap[key]
            self.handle_callback(callback, key)
        #Keycode streaming
        elif callable(self.streaming):
            self.handle_callback(self.streaming, key, pass_key=True)
        else:
            pass #No handler for the key
        
    def handle_callback(self, callback, key, pass_key=False):
        try:
            if pass_key:
                callback(key)
            else:
                callback()
        except Exception as e:
            print("Exception {} caused by callback {} when key {} was received".format(e, callback, key))
            print_exc()
        finally:
            return

    def listen(self):
        """Start event_loop in a thread. Nonblocking."""
        for driver in self.drivers.values():
            driver.start()
        self.listener_thread = Thread(target = self.event_loop, name="InputThread-"+str(self.thread_index), args=(self.thread_index, )) 
        self.thread_index += 1
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return True

    def stop_listen(self):
        """This sets a flag for ``event_loop`` to stop. It also calls a ``stop`` method of the input driver ``InputListener`` is using."""
        if self.stop_flag is not None:
            self.stop_flag.set()
        for driver in self.drivers.values():
            driver.stop()
        return True

    def atexit(self):
        """Exits driver (if necessary) if something wrong happened or ZPUI exits. Also, stops the listener"""
        self.stop_listen()
        for driver in self.drivers.values():
            if hasattr(driver, "atexit"):
                driver.atexit()
        try:
            self.listener_thread.join()
        except AttributeError:
            pass


class InputProxy():
    reserved_keys = ["KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN", "KEY_ENTER", "KEY_KPENTER"]

    def __init__(self):
        self.keymap = {}
        self.streaming = None
        self.maskable_keymap = {}
        self.nonmaskable_keymap = {}

    def set_streaming(self, callback):
        """Sets a callback for streaming key events. This callback will be called
        each time a key is pressed that doesn't belong to one of the three keymaps.

        The callback will be called  with key_name as first argument but should
        support arbitrary number of keyword arguments if compatibility with
        future versions is desired. (basically, add **kwargs to it).

        If a callback was set before, replaces it. The callbacks set will not be
        restored after being replaced by other callbacks. Care must be taken to
        make sure that the callback is only executed when the app or UI element
        that set it is active."""
        self.streaming = callback

    def remove_streaming(self):
        """Removes a callback for streaming key events, if previously set by any
        app/UI element. This is more of a convenience function, to avoid your
        callback being called when your app or UI element is not active."""
        self.streaming = None

    def set_callback(self, key_name, callback):
        """Sets a single callback of the listener."""
        self.keymap[key_name] = callback

    def check_special_callback(self, key_name):
        """Raises exceptions upon setting of a special callback on a reserved/taken keyname."""
        if key_name in self.reserved_keys:
            #Trying to set a special callback for a reserved key
            raise CallbackException(1, "Special callback for {} can't be set because it's one of the reserved keys".format(key_name))
        elif key_name in self.nonmaskable_keymap:
            #Key is already used in a non-maskable callback
            raise CallbackException(2, "Special callback for {} can't be set because it's already set as nonmaskable".format(key_name))
        elif key_name in self.maskable_keymap: 
            #Key is already used in a maskable callback
            raise CallbackException(3, "Special callback for {} can't be set because it's already set as maskable".format(key_name))

    def set_maskable_callback(self, key_name, callback):
        """Sets a single maskable callback of the listener. Raises `CallbackException`
        if the callback is one of the reserved keys or already is in maskable/nonmaskable
        keymap.

        A maskable callback is global (can be cleared) and will be called upon a keypress 
        unless a callback for the same keyname is already set in keymap."""
        self.check_special_callback(key_name)
        self.maskable_keymap[key_name] = callback

    def set_nonmaskable_callback(self, key_name, callback):
        """Sets a single nonmaskable callback of the listener. Raises `CallbackException`
        if the callback is one of the reserved keys or already is in maskable/nonmaskable
        keymap.

        A nonmaskable callback is global (never cleared) and will be called upon a keypress 
        even if a callback for the same keyname is already set in ``keymap``
        (callback from the ``keymap`` won't be called)."""
        self.check_special_callback(key_name)
        self.nonmaskable_keymap[key_name] = callback

    def remove_callback(self, key_name):
        """Removes a single callback of the listener."""
        self.keymap.pop(key_name)

    def remove_maskable_callback(self, key_name):
        """Removes a single maskable callback of the listener."""
        self.maskable_keymap.pop(key_name)

    def get_keymap(self):
        """Returns the current keymap."""
        return self.keymap

    def set_keymap(self, keymap):
        """Sets all the callbacks supplied, removing the previously set keymap completely."""
        self.keymap = keymap

    def replace_keymap_entries(self, keymap):
        """Sets all the callbacks supplied, not removing previously set
        but overwriting those with same keycodes."""
        for key in keymap.keys:
            set_callback(key, keymap[key])

    def clear_keymap(self):
        """Removes all the callbacks set."""
        self.keymap = {}


def init(input_configs):
    """ This function is called by main.py to read the input configuration,
    pick the corresponding drivers and initialize InputListener.
 
    It also sets ``listener`` globals of ``input`` module with the listener instance,
    as well as registers ``listener.atexit()`` function to be called when script exits."""
    drivers = {}
    for input_config in input_configs:
        driver_name = input_config["driver"]
        driver_module = importlib.import_module("input.drivers."+driver_name)
        args = input_config["args"] if "args" in input_config else []
        kwargs = input_config["kwargs"] if "kwargs" in input_config else {}
        driver = driver_module.InputDevice(*args, **kwargs)
        drivers[driver_name] = driver
    listener = InputListener(drivers)
    atexit.register(listener.atexit)
