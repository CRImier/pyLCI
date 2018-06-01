from traceback import format_exc
from threading import Thread, Event
from time import sleep
from copy import copy
import importlib

import atexit
import Queue
from helpers import setup_logger

import inspect

listener = None

logger = setup_logger(__name__, "warning")

class CallbackException(Exception):
    def __init__(self, errno=0, message=""):
        self.errno = errno
        self.message = message


class InputProcessor(object):
    """A class which listens for input device events and processes the callbacks 
    set in the InputProxy instance for the currently active context."""
    stop_flag = None
    thread_index = 0
    backlight_cb = None

    current_proxy = None
    proxy_methods = ["listen", "stop_listen"]
    proxy_attrs = ["available_keys"]

    def __init__(self, drivers, context_manager):
        self.global_keymap = {}
        self.drivers = drivers
        self.cm = context_manager
        self.queue = Queue.Queue()
        self.available_keys = {}
        for driver_name, driver in self.drivers.items():
            driver.send_key = self.receive_key #Overriding the send_key method so that keycodes get sent to InputListener
            self.available_keys[driver_name] = driver.available_keys
            driver.start()
        atexit.register(self.atexit)

    def receive_key(self, key):
        """ This is the method that receives keypresses from drivers and puts them into ``self.queue`` for ``self.event_loop`` to receive """
        try:
            self.queue.put(key)
        except:
            raise #Just collecting possible exceptions for now

    def attach_new_proxy(self, proxy):
        """
        Calls ``detach_proxy``, then ``attach_proxy`` - just a convenience wrapper.
        """
        self.detach_current_proxy()
        self.attach_proxy(proxy)

    def attach_proxy(self, proxy):
        """
        This method is to be called from the ContextManager. Saves a proxy
        internally, so that when a callback is received, its keymap can be
        referenced.
        """
        if self.current_proxy:
            raise ValueError("A proxy is already attached!")
        logger.info("Attaching proxy for context: {}".format(proxy.context_alias))
        self.current_proxy = proxy

    def detach_current_proxy(self):
        """
        This method is to be called from the ContextManager. Saves a proxy
        internally, so that when a callback is received, its keymap can be
        referenced.
        """
        if self.current_proxy:
            logger.info("Detaching proxy for context: {}".format(self.current_proxy.context_alias))
            self.current_proxy = None

    def get_current_proxy(self):
        return self.current_proxy

    def set_global_callback(self, key, callback):
        """
        Sets a global callback for a key. That global callback will be processed
        before the backlight callback or any proxy callbacks.
        """
        logger.info("Setting a global callback for key {}".format(key))
        if key in self.global_keymap.keys():
            #Key is already used in the global keymap
            raise CallbackException(4, "Global callback for {} can't be set because it's already in the keymap!".format(key_name))
        self.global_keymap[key] = callback

    def receive_key(self, key):
        """ This is the method that receives keypresses from drivers and puts
        them into ``self.queue``, to be processed by ``self.event_loop`` 
        Will block with full queue until the queue has a free spot.
        """
        self.queue.put(key)

    def event_loop(self, index):
        """
        Blocking event loop which just calls ``process_key`` once a key
        is received in the ``self.queue``. Also has some mechanisms that
        make sure the existing event_loop will exit once flag is set, even
        if other event_loop has already started (thought an event_loop can't
        exit if it's still processing a callback.)
        """
        logger.debug("Starting event loop "+str(index))
        self.stop_flag = Event()
        stop_flag = self.stop_flag # Saving a reference.
        # stop_flag is an object that will signal the current input thread to exit or not exit once it's done processing a callback.
        # It'll be called just before self.stop_flag will be overwritten. However, we've got a reference to it and now can check the exact flag this thread itself constructed.
        # Praise the holy garbage collector.
        stop_flag.clear()
        while not stop_flag.isSet():
            if self.get_current_proxy() is not None:
                try:
                    key = self.queue.get(False, 0.1)
                except Queue.Empty:
                    # here an active event_loop spends most of the time
                    sleep(0.1)
                except AttributeError:
                    # typically happens upon program termination
                    pass
                else:
                    # here event_loop is usually busy
                    self.process_key(key)
            else:
                # No current proxy set yet, not processing anything
                sleep(0.1)
        logger.debug("Stopping event loop "+str(index))

    def process_key(self, key):
        """
        This function receives a keyname, finds the corresponding callback/action
        and handles it. The lookup order is as follows:

            * Global callbacks - set on the InputProcessor itself
            * Proxy non-maskable callbacks
            * Backlight callback (doesn't do anything with the keyname, but dismisses the keypress if it turned on the backlight)
            * Proxy simple callbacks
            * Proxy maskable callbacks
            * Streaming callback (if set, just sends the key to it)

        As soon as a match is found, processes the associated callback and returns.
        """
        # Global and nonmaskable callbacks are supposed to work
        # even when the screen backlight is off
        #
        # First, querying global callbacks - they're more important than
        # even the current proxy nonmaskable callbacks
        logger.debug("Received key: {}".format(key))
        if key in self.global_keymap:
            callback = self.global_keymap[key]
            self.handle_callback(callback, key, type="global")
            return
        # Now, all the callbacks are either proxy callbacks or backlight-related
        # Saving a reference to current_proxy, in case it changes during the lookup
        current_proxy = self.get_current_proxy()
        if key in current_proxy.nonmaskable_keymap:
            callback = current_proxy.nonmaskable_keymap[key]
            self.handle_callback(callback, key, type="nonmaskable", context_name=current_proxy.context_alias)
            return
        # Checking backlight state, turning it on if necessary
        if callable(self.backlight_cb):
            try:
                # backlight_cb turns on the backligth as a side effect
                backlight_was_off = self.backlight_cb()
            except:
                logger.exception("Exception while calling the backlight check callback!")
            else:
                # If backlight was off, ignore the keypress
                if backlight_was_off is True:
                    return
        # Now, all the other callbacks of the proxy:
        # Simple callbacks
        if key in current_proxy.keymap:
            callback = current_proxy.keymap[key]
            self.handle_callback(callback, key, context_name=current_proxy.context_alias)
        #Maskable callbacks
        elif key in current_proxy.maskable_keymap:
            callback = current_proxy.maskable_keymap[key]
            self.handle_callback(callback, key, type="maskable", context_name=current_proxy.context_alias)
        #Keycode streaming
        elif callable(current_proxy.streaming):
            self.handle_callback(current_proxy.streaming, key, pass_key=True, type="streaming", context_name=current_proxy.context_alias)
        else:
            logger.debug("Key {} has no handlers - ignored!".format(key))
            pass #No handler for the key
        
    def handle_callback(self, callback, key, pass_key=False, type="simple", context_name=None):
        try:
            if context_name:
                logger.info("Processing a {} callback for key {}, context {}".format(type, key, context_name))
            else:
                logger.info("Processing a {} callback for key {}".format(type, key))
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
            logger.error("Locals of the callback:")
            logger.error(locals)
        finally:
            return

    def listen(self):
        """Start event_loop in a thread. Nonblocking."""
        self.processor_thread = Thread(target = self.event_loop, name="InputThread-"+str(self.thread_index), args=(self.thread_index, ))
        self.thread_index += 1
        self.processor_thread.daemon = True
        self.processor_thread.start()

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
            self.processor_thread.join()
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
        for attr_name in self.proxy_attrs:
            setattr(proxy, attr_name, copy(getattr(self, attr_name)))


class InputProxy(object):
    reserved_keys = ["KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN", "KEY_ENTER"]

    def __init__(self, context_alias):
        self.keymap = {}
        self.streaming = None
        self.maskable_keymap = {}
        self.nonmaskable_keymap = {}
        self.context_alias = context_alias

    def set_streaming(self, callback):
        """
        Sets a callback for streaming key events. This callback will be called
        each time a key is pressed that doesn't belong to one of the three keymaps.

        The callback will be called  with key_name as first argument but should
        support arbitrary number of keyword arguments if compatibility with
        future versions is desired. (basically, add ``**kwargs`` to it).

        If a callback was set before, replaces it. The callbacks set will not be
        restored after being replaced by other callbacks. Care must be taken to
        make sure that the callback is only executed when the app or UI element
        that set it is active.
        """
        self.streaming = callback

    def remove_streaming(self):
        """
        Removes a callback for streaming key events, if previously set by any
        app/UI element. This is more of a convenience function, to avoid your
        callback being called when your app or UI element is not active.
        """
        self.streaming = None

    def set_callback(self, key_name, callback):
        """
        Sets a single callback.

        >>> i = InputProxy("test")
        >>> i.clear_keymap()
        >>> i.set_callback("KEY_ENTER", lambda: None)
        >>> "KEY_ENTER" in i.keymap
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
        """Sets a single maskable callback. Raises ``CallbackException``
        if the callback is one of the reserved keys or already is in maskable/nonmaskable
        keymap.

        A maskable callback is global (can be cleared) and will be called upon a keypress 
        unless a callback for the same keyname is already set in ``keymap``."""
        self.check_special_callback(key_name)
        self.maskable_keymap[key_name] = callback

    def set_nonmaskable_callback(self, key_name, callback):
        """Sets a single nonmaskable callback. Raises ``CallbackException``
        if the callback is one of the reserved keys or already is in maskable/nonmaskable
        keymap.

        A nonmaskable callback is global (never cleared) and will be called upon a keypress 
        even if a callback for the same keyname is already set in ``keymap``
        (callback from the ``keymap`` won't be called)."""
        self.check_special_callback(key_name)
        self.nonmaskable_keymap[key_name] = callback

    def remove_callback(self, key_name):
        """Removes a single callback."""
        self.keymap.pop(key_name)

    def remove_maskable_callback(self, key_name):
        """Removes a single maskable callback."""
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

        >>> i = InputProxy("test")
        >>> i.set_keymap({"KEY_LEFT":lambda:1, "KEY_DOWN":lambda:2})
        >>> i.keymap["KEY_LEFT"]()
        1
        >>> i.keymap["KEY_DOWN"]()
        2
        >>> i.update_keymap({"KEY_LEFT":lambda:3, "KEY_1":lambda:4})
        >>> i.keymap["KEY_LEFT"]()
        3
        >>> i.keymap["KEY_DOWN"]()
        2
        >>> i.keymap["KEY_1"]()
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
    doctest.testmod()
