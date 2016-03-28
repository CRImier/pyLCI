import evdev
from evdev import ecodes
import pifacecad
import threading

class InputDevice():
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
        self.name = name
        self.cad = pifacecad.PiFaceCAD()
        self.listener = pifacecad.SwitchEventListener(chip=self.cad)
        for i in range(8):
            self.listener.register(i, pifacecad.IODIR_FALLING_EDGE, self.press_key)
    
    def start(self):
        self.listener.activate()

    def stop(self):
        self.listener.deactivate()

    def press_key(self, event):
        keycode = self.mapping[event.pin_num]
        self.send_key(keycode)

    def send_key(self, keycode):
        print(keycode)

    def activate(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()
