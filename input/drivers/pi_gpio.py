import RPi.GPIO as GPIO
import threading
from time import sleep

class InputDevice():
    """ A driver for pushbuttons attached to Raspberry Pi GPIO. It uses RPi.GPIO library. First button's pin has to be attached to ground, second has to be attached to the GPIO pin and pulled up to 3.3V with a 1-10K resistor."""

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
        """Initialises the ``InputDevice`` object. """
        pass


    def start(self):
        """Polling loop. Stops when ``stop_flag`` is set to True."""
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
                sleep(0.01)
        except:
            raise
        finally:
            GPIO.cleanup()

    def stop(self):
        """Sets the ``stop_flag`` for loop functions."""
        self.stop_flag = True

    def send_key(self, keycode):
        """A hook to be overridden by ``InputListener``. Otherwise, prints out key names as soon as they're pressed so is useful for debugging."""
        print(keycode)

    def activate(self):
        """Starts a thread with ``start`` function as target."""
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = True
        self.thread.start()
