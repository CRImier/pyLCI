from traceback import print_exc, format_exc
from threading import Thread, Event
from time import sleep
import importlib
import logging
import atexit
import Queue
import sys

import inspect

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class CallbackException(Exception):
    def __init__(self, errno=0, message=""):
        self.errno = errno
        self.message = message


class InputProcessor():
    """A class which listens for input device events and processes the callbacks 
    set in the InputProxy instance for the currently active context."""
    stop_flag = None
    thread_index = 0
    backlight_cb = None

    current_proxy = None
    proxy_methods = ["listen", "stop_listen"]

    def __init__(self, drivers, context_manager):
        self.drivers = drivers
        self.cm = context_manager
        self.queue = Queue.Queue()
        for driver in self.drivers.values():
            driver.send_key = self.receive_key #Overriding the send_key method so that keycodes get sent to InputListener
            driver.start()
        atexit.register(self.atexit)

    def attach_proxy(self, proxy):
        if self.current_proxy:
            raise ValueError("A proxy is already attached!")
        logger.info("Attaching proxy for context: {}".format(proxy.context_alias))
        self.current_proxy = proxy

    def detach_current_proxy(self):
        if self.current_proxy:
            logger.info("Detaching proxy for context: {}".format(self.current_proxy.context_alias))
            self.current_proxy = None

    def get_current_proxy(self):
        return self.current_proxy

    def receive_key(self, key):
        """ This is the method that receives keypresses from drivers and puts
        them into ``self.queue``, to be processed by ``self.event_loop`` 
        Will block with full queue, until the queue will have a free spot."""
        self.queue.put(key)

    def event_loop(self, index):
        """Blocking event loop which just calls callbacks in the keymap
        once corresponding keys are received in the ``self.queue``."""
        logger.debug("Starting event loop "+str(index))
        self.stop_flag = Event()
        stop_flag = self.stop_flag #Saving a reference.
        #stop_flag is an object that will signal the current input thread to exit or not exit once it's done processing a callback.
        #It'll be called just before self.stop_flag will be overwritten. However, we've got a reference to it and now can check the exact object this thread itself constructed.
        #Praise the holy garbage collector.
        stop_flag.clear()
        while not stop_flag.isSet():
            if self.get_current_proxy() is not None:
                try:
                    key = self.queue.get(False, 0.1)
                except Queue.Empty:
                    sleep(0.1)
                except AttributeError:
                    pass #Typically happens if InputListener exits abnormally upon program termination
                else:
                    self.process_key(key)
            else:
                #No current proxy set yet, not processing anything
                sleep(0.1)
        logger.debug("Stopping event loop "+str(index))

    def process_key(self, key):
        #Could probably be optimised in some way, that is, not doing dictionary lookup 
        #each time a key is pressed
        current_proxy = self.get_current_proxy()
        #Nonmaskable callbacks are supposed to work even when the screen backlight is off
        #(especially since, right now, they're actions like "volume up/down" and "next song")
        if key in current_proxy.nonmaskable_keymap:
            callback = current_proxy.nonmaskable_keymap[key]
            self.handle_callback(callback, key)
            return
        #Checking backlight state, turning it on if necessary
        if callable(self.backlight_cb):
            try:
                backlight_was_off = self.backlight_cb()
            except:
                logger.warning("Exception while calling the backlight check callback!")
                logger.warning(format_exc())
            else:
                #If backlight was off, ignore the keypress
                if backlight_was_off is True:
                    return
        #Now, all the other options:
        #Simple callbacks
        if key in current_proxy.keymap:
            callback = current_proxy.keymap[key]
            self.handle_callback(callback, key)
        #Maskable callbacks
        elif key in current_proxy.maskable_keymap:
            callback = current_proxy.maskable_keymap[key]
            self.handle_callback(callback, key)
        #Keycode streaming
        elif callable(current_proxy.streaming):
            self.handle_callback(current_proxy.streaming, key, pass_key=True)
        else:
            pass #No handler for the key
        
    def handle_callback(self, callback, key, pass_key=False):
        try:
            logger.info("Processing a callback for key {}".format(key))
            logger.debug("pass_key = {}".format(pass_key))
            logger.debug("callback name: {}".format(callback.__name__))
            if pass_key:
                callback(key)
            else:
                callback()
        except Exception as e:
            locals = inspect.trace()[-1][0].f_locals
            logger.error("Exception {} caused by callback {} when key {} was received".format(e.__str__() or e.__class__, callback, key))
            logger.error(format_exc())
            logger.error("Locals:")
            logger.error(locals)
        finally:
            return

    def listen(self):
        """Start event_loop in a thread. Nonblocking."""
        self.listener_thread = Thread(target = self.event_loop, name="InputThread-"+str(self.thread_index), args=(self.thread_index, )) 
        self.thread_index += 1
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def stop_listen(self):
        """This sets a flag for ``event_loop`` to stop. If the ``event_loop()`` is 
        currently executing a callback, it will exit as soon as the callback will 
        finish executing."""
        if self.stop_flag is not None:
            self.stop_flag.set()

    def atexit(self):
        """Exits driver (if necessary) if something wrong happened or ZPUI exits. Also, stops the InputProcessor, and all the associated drivers."""
        self.stop_listen()
        for driver in self.drivers.values():
            driver.stop()
            if hasattr(driver, "atexit"):
                driver.atexit()
        try:
            self.listener_thread.join()
        except AttributeError:
            pass

    def proxy_method(self, method_name, context_alias, *args, **kwargs):
        if context_alias == self.cm.get_current_context():
            logger.debug("Calling method \"{}\" for proxy \"{}\"".format(method_name, context_alias))
            getattr(self, method_name)(*args, **kwargs)
        else:
            logger.debug("Not calling method \"{}\" for proxy \"{}\" since it's not current".format(method_name, context_alias))
            pass #Ignoring method calls from non-current proxies for now

    def register_proxy(self, proxy):
        context_alias = proxy.context_alias
        for method_name in self.proxy_methods:
            setattr(proxy, method_name, lambda x=method_name, y=context_alias, *a, **k: self.proxy_method(x, y, *a, **k))


class InputProxy():
    reserved_keys = ["KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN", "KEY_ENTER", "KEY_KPENTER"]

    def __init__(self, context_alias):
        self.keymap = {}
        self.streaming = None
        self.maskable_keymap = {}
        self.nonmaskable_keymap = {}
        self.context_alias = context_alias

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
        """
        Sets a single callback of the listener.

        >>> self.clear_keymap()
        >>> self.set_callback("KEY_ENTER", lambda: None)
        >>> "KEY_ENTER" in self.keymap
        True
        """
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
        """Sets a single maskable callback of the listener. Raises ``CallbackException``
        if the callback is one of the reserved keys or already is in maskable/nonmaskable
        keymap.

        A maskable callback is global (can be cleared) and will be called upon a keypress 
        unless a callback for the same keyname is already set in ``keymap``."""
        self.check_special_callback(key_name)
        self.maskable_keymap[key_name] = callback

    def set_nonmaskable_callback(self, key_name, callback):
        """Sets a single nonmaskable callback of the listener. Raises ``CallbackException``
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

    def set_keymap(self, new_keymap):
        """Sets all the callbacks supplied, removing the previously set keymap completely."""
        self.keymap = new_keymap

    def update_keymap(self, new_keymap):
        """
        Updates the InputProxy keymap with entries from another keymap.
        Will add/replace callbacks for keys in the new keymap,
        but will leave the existing keys that are not in new keymap intact

        >>> self.set_keymap({"KEY_LEFT":lambda:1, "KEY_DOWN":lambda:2})
        >>> self.keymap["KEY_LEFT"]()
        1
        >>> self.keymap["KEY_DOWN"]()
        2
        >>> self.update_keymap({"KEY_LEFT":lambda:3, "KEY_1":lambda:4})
        >>> self.keymap["KEY_LEFT"]()
        3
        >>> self.keymap["KEY_DOWN"]()
        2
        >>> self.keymap["KEY_1"]()
        4
        """
        self.keymap.update(new_keymap)

    def clear_keymap(self):
        """Removes all the callbacks set."""
        self.keymap = {}


def init(driver_configs, context_manager):
    """ This function is called by main.py to read the input configuration,
    pick the corresponding drivers and initialize InputProcessor. Returns 
    the InputProcessor instance created.`"""
    drivers = {}
    for driver_config in driver_configs:
        driver_name = driver_config["driver"]
        driver_module = importlib.import_module("input.drivers."+driver_name)
        args = driver_config.get("args", [])
        kwargs = driver_config.get("kwargs", {})
        driver = driver_module.InputDevice(*args, **kwargs)
        drivers[driver_name] = driver
    return InputProcessor(drivers, context_manager)

if __name__ == "__main__":
    import doctest
    doctest.testmod(extraglobs={'self': InputProxy("test")})
