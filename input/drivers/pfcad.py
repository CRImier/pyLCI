import pifacecad
import threading

class InputDevice():
    """ A driver for PiFace Control and Display Raspberry Pi shields. It has 5 buttons, one single-axis joystick with a pushbutton, a 16x2 HD44780 screen and an IR receiver (not used yet)."""
    mapping = [
    "KEY_LEFT",
    "KEY_RIGHT",
    "KEY_HOME",
    "KEY_END",
    "KEY_DELETE",
    "KEY_KPENTER",
    "KEY_UP",
    "KEY_DOWN"]
    
    def __init__(self):
        """Initialises the ``InputDevice`` object. Also, registers callbacks to ``press_key`` method. """
        self.cad = pifacecad.PiFaceCAD()
        self.listener = pifacecad.SwitchEventListener(chip=self.cad)
        for i in range(8):
            self.listener.register(i, pifacecad.IODIR_FALLING_EDGE, self.press_key)
    
    def start(self):
        """Starts ``pifacecad.SwitchEventListener``. Is blocking."""
        self.listener.activate()

    def stop(self):
        """Stops ``pifacecad.SwitchEventListener``."""
        self.listener.deactivate()

    def press_key(self, event):
        """Converts event numbers to keycodes using ``mapping`` and sends them to ``send_key``. Is a callback for ``SwitchEventListener``."""
        keycode = self.mapping[event.pin_num]
        self.send_key(keycode)

    def send_key(self, keycode):
        """A hook to be overridden by ``InputListener``. Otherwise, prints out key names as soon as they're pressed so is useful for debugging."""
        print(keycode)

    def activate(self):
        """Starts a thread with ``start`` function as target."""
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()
