import smbus
from time import sleep

from skeleton import InputSkeleton

class InputDevice(InputSkeleton):
    default_mapping = [
    "KEY_UP",
    "KEY_DOWN",
    "KEY_RIGHT",
    "KEY_ENTER",
    "KEY_1",
    "KEY_2",
    "KEY_3",
    "KEY_4",
    "KEY_5",
    "KEY_6",
    "KEY_7",
    "KEY_8",
    "KEY_9",
    "KEY_*",
    "KEY_0",
    "KEY_#",
    "KEY_F1",
    "KEY_F2",
    "KEY_ANSWER",
    "KEY_HANGUP",
    "KEY_PAGEUP",
    "KEY_PAGEDOWN",
    "KEY_F5",
    "KEY_F6",
    "KEY_VOLUMEUP",
    "KEY_VOLUMEDOWN",
    "KEY_PROG1",
    "KEY_PROG2",
    "KEY_CAMERA",
    "KEY_LEFT"
    ]

    def __init__(self, addr = 0x12, bus = 1, int_pin = 21, **kwargs):
        """Initialises the ``InputDevice`` object.  
                                                                               
        Kwargs:                                                                  
                                                                                 
            * ``bus``: I2C bus number.
            * ``addr``: I2C address of the device.
            * ``int_pin``: GPIO pin for interrupt mode. 

        """
        self.bus_num = bus
        self.bus = smbus.SMBus(self.bus_num)
        if type(addr) in [str, unicode]:
            addr = int(addr, 16)
        self.addr = addr
        self.int_pin = int_pin
        self.init_expander()
        InputSkeleton.__init__(self, **kwargs)

    def init_expander(self):
        try:
            self.bus.read_byte(self.addr)
        except IOError:
            return True
        else:
            return False

    def runner(self):
        """Runs either interrupt-driven or polling loop."""
        self.stop_flag = False
        if self.int_pin is None:
            self.loop_polling()
        else:
            self.loop_interrupts()

    def loop_interrupts(self):
        """Interrupt-driven loop. Currently can only use ``RPi.GPIO`` library. Stops when ``stop_flag`` is set to True."""
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(self.int_pin, GPIO.IN)
        while not self.stop_flag:
            while GPIO.input(self.int_pin) == False and self.enabled:
                data = self.bus.read_byte(self.addr)
                self.send_key(self.mapping[data-1])
            sleep(0.1)

if __name__ == "__main__":
    id = InputDevice(addr = 0x12, int_pin = 21, threaded=False)
    id.runner()
