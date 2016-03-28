import evdev
from evdev import ecodes
import RPi.GPIO as GPIO
import threading
import atexit

class InputDevice():
    button_pins = [18, 23, 24, 25, 22, 27, 17, 4]
    mapping = [
    "KEY_LEFT",
    "KEY_RIGHT",
    "KEY_HOME",
    "KEY_END",
    "KEY_DELETE",
    "KEY_KPENTER",
    "KEY_UP",
    "KEY_DOWN"]
    stop_flag = False
    
    def __init__(self):
        pass

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
                            self.send_key(key)
                        button_states[i] = button_state
        except:
            raise
        finally:
            GPIO.cleanup()

    def stop(self):
        self.stop_flag = True

    def send_key(self, key):
        print(key)

    def activate(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = True
        self.thread.start()
