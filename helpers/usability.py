from __future__ import print_function
from threading import Event

class ExitHelper(object):
    """
    A simple helper for loops, to allow exiting them on pressing KEY_LEFT (or other keys).

    You need to make sure that, while the loop is running, no other UI element
    sets its callbacks. with Printer UI elements, you can usually pass None
    instead of ``i`` to achieve that.

    Arguments:

        * ``i``: input device
        * ``keys``: all the keys that should trigger an exit. You can also pass "*" so that
          it catches all of the keys (allowing you to make an "exit on any key" action).
        * ``cb``: the callback that should be executed once one of the keys is pressed.
          By default, sets an internal flag that you can check with ``do_exit`` and
          ``do_run``.
    """

    started = False
    callback = None

    def __init__(self, i, keys=["KEY_LEFT"], cb=None):
        self.i = i
        self.keys = keys
        self._do_exit = Event()
        self.set_callback(cb)

    def start(self):
        """
        Sets up the input listener, then returns ``self`` (allowing for shortened usage,
        like ``eh = ExitHelper(i).start()``.
        """
        self.setup_input()
        self.started = True
        return self

    def setup_input(self):
        """Clears input device keymap, registers callbacks and enables input listener."""
        self.i.stop_listen()
        self.i.clear_keymap()
        if "*" in self.keys:
            self.i.set_streaming(lambda *args: self.callback())
        else:
            keymap = {key:self.callback for key in self.keys}
            self.i.set_keymap(keymap)
        self.i.listen()

    def set_callback(self, callback=None):
        if callback is None:
            self.callback = self.signal_exit
        elif not callable(callback):
            raise ArgumentError("set_callback expected a callable, received {}!".format(type(callback)))
        else:
            def wrapper():
                self._do_exit.set()
                callback()
            self.callback = wrapper

    def do_exit(self):
        """Returns ``True`` once exit flag has been set, ``False`` otherwise."""
        return self._do_exit.isSet()

    def do_run(self):
        """Returns ``False`` once exit flag has been set, ``True`` otherwise."""
        return not self._do_exit.isSet()

    def signal_exit(self):
        self._do_exit.set()

    def reset(self):
        """Clears the exit flag."""
        self._do_exit.clear()

    def stop(self):
        """Stop input listener and remove the created keymap. Shouldn't usually be necessary,
        since all other UI elements are supposed to make sure their callbacks are set."""
        self.started = False
        self.i.clear_keymap()
        self.i.stop_listen()
