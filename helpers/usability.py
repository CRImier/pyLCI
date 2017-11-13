from __future__ import print_function
from threading import Event

class ExitHelper():
    """A simple helper for loops, to allow exiting them on pressing KEY_LEFT (or other keys).

    You need to make sure that, while the loop is running, no other UI element 
    sets its callbacks. with Printer UI elements, you can usually pass None
    instead of ``i`` to achieve that.

    Arguments:

        * ``i``: input device
        * ``keys``: all the keys that should trigger an exit"""

    started = False

    def __init__(self, i, keys=["KEY_LEFT"]):
        self.i = i
        self.keys = keys
        self._do_exit = Event()

    def start(self):
        """Clears input device keymap, registers callbacks and enables input listener."""
        self.i.stop_listen()
        self.i.clear_keymap()
        keymap = {key:self.signal_exit for key in self.keys}
        self.i.set_keymap(keymap)
        self.i.listen()
        self.started = True
        return self #Allows shortened usage, like eh = ExitHelper(i).start()

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
