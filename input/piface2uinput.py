import evdev
from evdev import ecodes
import pifacecad
import threading
import atexit

class Listener():
    def __init__(self):
        self.uinput = evdev.UInput(name='piface-uinput', devnode='/dev/uinput')
        self.cad = pifacecad.PiFaceCAD()
        self.listener = pifacecad.SwitchEventListener(chip=self.cad)
        atexit.register(self.listener.deactivate)
        for i in range(8):
            self.listener.register(i, pifacecad.IODIR_FALLING_EDGE, self.press_key)
        self.mapping = [
        ecodes.KEY_LEFT,
        ecodes.KEY_RIGHT,
        ecodes.KEY_HOME,
        ecodes.KEY_END,
        ecodes.KEY_DELETE,
        ecodes.KEY_KPENTER,
        ecodes.KEY_UP,
        ecodes.KEY_DOWN]
    
    def start(self):
        self.listener.activate()

    def press_key(self, event):
        print event.pin_num
        key = self.mapping[event.pin_num]
        self.uinput.write(ecodes.EV_KEY, key, 1)
        self.uinput.write(ecodes.EV_KEY, key, 0)
        self.uinput.syn()

    def start_thread(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()

    def __del__(self):
        print "Closing"
        self.listener.deactivate()


if __name__=="__main__":
    listener = Listener()
    listener.start()
