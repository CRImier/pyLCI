import threading
from copy import copy

from helpers import setup_logger
logger = setup_logger(__name__, "warning")

class InputSkeleton(object):
    """Base class for input devices. Expectations from children:

    * ``self.default_mapping`` variable to be set unless you're always going to pass mapping as argument in config
    * ``self.runner`` to be set to a function that'll run in backround, scanning for button presses and sending events to send_key
    * main thread to stop sending keys if self.enabled is False
    * main thread to exit immediately if self.stop_flag is True"""

    enabled = True
    stop_flag = False
    available_keys = None
    status_available = False

    def __init__(self, mapping=None, threaded=True, conn_check_sleep=1):
        self.connection_check_sleep = conn_check_sleep
        self.connected = threading.Event()
        if mapping is not None:
            self.mapping = mapping
        else:
            self.mapping = self.default_mapping
        self.connect(initial=True)
        self.set_available_keys()
        if threaded:
            self.start_thread()
        # A flag that avoids littering the logs when probing the device fails
        self.init_hw_error_msg_filter = False

    def try_init_hardware(self, initial=False):
        try:
            value = self.init_hw()
            self.init_hw_error_msg_filter = False
            return value
        except IOError:
            if self.connected.isSet() or initial:
                logger.exception("Cannot find hardware")
            return False
        except AttributeError:
            raise
        except Exception as e:
            if not self.init_hw_error_msg_filter:
                logger.exception("Unexpected exception while setting up hardware")
                self.init_hw_error_msg_filter = True
            return False

    def start(self):
        """Sets the ``enabled`` for loop functions to start sending keycodes."""
        self.enabled = True

    def set_available_keys(self):
        """
        A simple ``i.available_keys``-setting code that assumes the driver's mapping is a plain
        list of key names. If it's not so, the driver needs to override the
        ``set_available_keys`` method to properly generate the ``available_keys`` list.
        """
        if not hasattr(self, "mapping"):
            logger.warning("mapping not available - the HID driver is used?")
            logger.warning("available_keys property set to None!")
            self.available_keys = None
            return
        if type(self.mapping) not in (list, tuple):
            raise ValueError("Can't use mapping as available_keys - not a list/tuple!")
        if not all([isinstance(el, basestring) for el in self.mapping]):
            raise ValueError("Can't use mapping as a capability if it's not a list of strings!")
        if not all([el.startswith("KEY_") for el in self.mapping]):
            nonkey_items = [el for el in self.mapping if not el.startswith("KEY_")]
            raise ValueError("Can't use mapping as a capability if its elements don't start with \"KEY_\"! (non-KEY_ items: {})".format(nonkey_items))
        self.available_keys = copy(list(self.mapping))

    def stop(self):
        """Unsets the ``enabled`` for loop functions to stop sending keycodes."""
        self.enabled = False

    def send_key(self, key):
        """A hook to be overridden by ``InputListener``. Otherwise, prints out key names as soon as they're pressed so is useful for debugging (to test things, just launch the driver as ``python driver.py``)"""
        logger.debug(key)

    def start_thread(self):
        """Starts a thread with ``start`` function as target."""
        self.thread = threading.Thread(target=self.runner, name="{} driver thread".format(self.__module__.rsplit('.', 1)[-1]))
        self.thread.daemon = True
        self.thread.start()

    def is_connected(self):
        if self.status_available:
            return None
        return self.connected.isSet()

    def check_connection(self):
        if self.status_available:
            status = self.connected.isSet()
            if not status:
                return self.connect()
            return True
        return True

    def connect(self, initial=False):
        status = None
        try:
            status = self.try_init_hardware(initial=False)
        except AttributeError:
            logger.error("{}: init_hw function not found!".format(self.__class__))
        if status is not None and self.status_available:
            if status:
                self.connected.set()
                return True
            else:
                self.connected.clear()
                return False
        return True

    def atexit(self):
        self.stop_flag = True
