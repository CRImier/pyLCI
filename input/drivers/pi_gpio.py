import evdev
from evdev import ecodes
import RPi.GPIO as GPIO
import threading
import atexit

class InputDevice():
    button_pins = [18, 23, 24, 25, 22, 27, 17, 4]
    mapping = [
    ecodes.KEY_LEFT,
    ecodes.KEY_RIGHT,
    ecodes.KEY_HOME,
    ecodes.KEY_END,
    ecodes.KEY_DELETE,
    ecodes.KEY_KPENTER,
    ecodes.KEY_UP,
    ecodes.KEY_DOWN]
    stop_flag = False
    
    def __init__(self, name='gpio-uinput'):
        self.name = name
        self.uinput = evdev.UInput({ecodes.EV_KEY:self.mapping}, name=name, devnode='/dev/uinput')

    def start(self):
        self.stop_flag = False
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        for pin_num in self.button_pins:
            GPIO.setup(pin_num, GPIO.IN) # Button pin set as input
        button_states = []
        for i, pin_num in enumerate(self.button_pins):
            button_states.append(GPIO.input(pin_num))
        try:
            while not self.stop_flag:
                for i, pin_num in enumerate(self.button_pins):
                    button_state = GPIO.input(pin_num)
                    if button_state != button_states[i]: # button state is changed
                        if button_state == True:
                            print("Button {} released".format(i+1))
                        else:
                            print("Button {} pressed".format(i+1))
                            key = self.mapping[i]
                            self.press_key(key)
                        button_states[i] = button_state
        except:
            raise
        finally:
            GPIO.cleanup()

    def stop(self):
        self.stop_flag = True

    def press_key(self, key):
        self.uinput.write(ecodes.EV_KEY, key, 1)
        self.uinput.write(ecodes.EV_KEY, key, 0)
        self.uinput.syn()

    def activate(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = True
        self.thread.start()

#    def __del__(self):
#       self.stop()




"""        else: # button is pressed:
            GPIO.output(ledPin, GPIO.HIGH)
            time.sleep(0.075)"""

