import smbus
from time import sleep
import threading

class InputDevice():
    """ A driver for PCF8574-based I2C IO expanders. They have 8 IO pins available as well as an interrupt pin. This driver treats all 8 pins as button pins, which is often the case. 

    It supports both interrupt-driven mode (as fr now, RPi-only) and polling mode."""

    mapping = [
    "KEY_DOWN",
    "KEY_UP",
    "KEY_KPENTER",
    "KEY_LEFT",
    "KEY_HOME",
    "KEY_END",
    "KEY_RIGHT",
    "KEY_DELETE"]
    stop_flag = False
    previous_data = 0

    def __init__(self, addr = 0x27, bus = 1, int_pin = None):
        """Initialises the ``InputDevice`` object.  
                                                                               
        Kwargs:                                                                  
                                                                                 
            * ``bus``: I2C bus number.
            * ``sleep_time``: I2C address of the expander.
            * ``skippable``: GPIO pin to which INT pin of the expander is connected. If supplied, interrupt-driven mode is used, otherwise, library reverts to polling mode.

        """
        self.bus_num = bus
        self.bus = smbus.SMBus(self.bus_num)
        self.addr = addr
        self.int_pin = int_pin

    def start(self):
        """Starts listening on the input device. Initialises the IO expander and runs either interrupt-driven or polling loop."""
        self.stop_flag = False
        self.bus.write_byte(self.addr, 0xff)
        if self.int_pin is None:
            self.loop_polling()
        else:
            self.loop_interrupts()

    def loop_interrupts(self):
        """Interrupt-driven loop. Currently can only use ``RPi.GPIO`` library. Stops when ``stop_flag`` is set to True."""
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(self.int_pin, GPIO.IN)
        button_states = []
        try:
            while not self.stop_flag:
                while GPIO.input(self.int_pin) == False:
                    data = (~self.bus.read_byte(self.addr)&0xFF)
                    self.process_data(data)
                    self.previous_data = data
                sleep(0.1)
        except:
            raise
        finally:
            GPIO.cleanup()

    def loop_polling(self):
        """Polling loop. Stops when ``stop_flag`` is set to True."""
        button_states = []
        while not self.stop_flag:
            data = (~self.bus.read_byte(self.addr)&0xFF)
            print(data)
            if data != self.previous_data:
                self.process_data(data)
                self.previous_data = data
            sleep(0.01)

    def process_data(self, data):
        """Checks data received from IO expander and classifies changes as either "button up" or "button down" events. On "button up", calls send_key with the corresponding button name from ``self.mapping``. """
        data_difference = data ^ self.previous_data
        changed_buttons = []
        for i in range(8):
            if data_difference & 1<<i:
                changed_buttons.append(i)
        for button_number in changed_buttons:
            if not data & 1<<button_number:
                self.send_key(self.mapping[button_number])

    def stop(self):
        """Sets the ``stop_flag`` for loop functions."""
        self.stop_flag = True

    def send_key(self, key):
        """A hook to be overridden by ``InputListener``. Otherwise, prints out key names as soon as they're pressed so is useful for debugging."""
        print(key)

    def activate(self):
        """Starts a thread with ``start`` function as target."""
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()


if __name__ == "__main__":
    id = InputDevice(addr = 0x3f)
    id.start()
