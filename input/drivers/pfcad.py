import pifacecad

from time import sleep
import atexit

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
    active=False
    busy=False
    
    def __init__(self):
        """Initialises the ``InputDevice`` object and starts ``pifacecad.SwitchEventListener``. Also, registers callbacks to ``press_key`` method. """
        self.cad = pifacecad.PiFaceCAD()
        self.listener = pifacecad.SwitchEventListener(chip=self.cad)
        for i in range(8):
            self.listener.register(i, pifacecad.IODIR_FALLING_EDGE, self.press_key)
        self.listener.activate()
        atexit.register(self.atexit)
    
    def start(self):
        """Does nothing as it's not easy to stop SwitchEventListener and be able to start it afterwards. Sets a flag for press_key, though."""
        self.active = True

    def stop(self):
        """Does nothing as it's not easy to stop SwitchEventListener and be able to start it afterwards. Unsets a flag for press_key, though."""
        self.active = False

    def press_key(self, event):
        """Converts event numbers to keycodes using ``mapping`` and sends them to ``send_key``. Is a callback for ``SwitchEventListener``."""
        if self.active:
            keycode = self.mapping[event.pin_num]
            while self.busy:
                sleep(0.01)
            self.busy = True
            self.send_key(keycode)
            self.busy = False

    def send_key(self, keycode):
        """A hook to be overridden by ``InputListener``. Otherwise, prints out key names as soon as they're pressed so is useful for debugging."""
        print(keycode)

    def activate(self):
        """Just sets the flag, listener is already running from the very start"""
        self.start()

    def atexit(self):
        """Deactivates the listener"""
        self.listener.deactivate()


if __name__ == "__main__":
    id = InputDevice()
    id.activate()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        id.listener.deactivate()

