import evdev
from evdev import ecodes
import pifacecad
import threading
import atexit


class InputDevice():
    mapping = [
    ecodes.KEY_LEFT,
    ecodes.KEY_RIGHT,
    ecodes.KEY_HOME,
    ecodes.KEY_END,
    ecodes.KEY_DELETE,
    ecodes.KEY_KPENTER,
    ecodes.KEY_UP,
    ecodes.KEY_DOWN]
    
    def __init__(self, name='piface-uinput'):
        self.name = name
        self.uinput = evdev.UInput({ecodes.EV_KEY:self.mapping}, name=self.name, devnode='/dev/uinput')
        self.cad = pifacecad.PiFaceCAD()
        self.listener = pifacecad.SwitchEventListener(chip=self.cad)
        atexit.register(self.listener.deactivate)
        for i in range(8):
            self.listener.register(i, pifacecad.IODIR_FALLING_EDGE, self.press_key)
    
    def start(self):
        self.listener.activate()

    def stop(self):
        self.listener.deactivate()

    def press_key(self, event):
        key = self.mapping[event.pin_num]
        self.uinput.write(ecodes.EV_KEY, key, 1)
        self.uinput.write(ecodes.EV_KEY, key, 0)
        self.uinput.syn()

    def activate(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()
