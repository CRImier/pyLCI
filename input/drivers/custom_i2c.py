import smbus
from time import sleep

from helpers import setup_logger
from skeleton import InputSkeleton
logger = setup_logger(__name__, "warning")

class InputDevice(InputSkeleton):
    default_mapping = [
    "KEY_LEFT",
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
    "KEY_CAMERA"
    ]

    status_available = True

    def __init__(self, addr = 0x12, bus = 1, int_pin = 16, **kwargs):
        """Initialises the ``InputDevice`` object.

        Kwargs:

            * ``bus``: I2C bus number.
            * ``addr``: I2C address of the device.
            * ``int_pin``: GPIO pin for interrupt mode.

        """
        self.bus_num = bus
        if isinstance(addr, basestring):
            addr = int(addr, 16)
        self.addr = addr
        self.int_pin = int_pin
        InputSkeleton.__init__(self, **kwargs)

    def init_hw(self):
        self.bus = smbus.SMBus(self.bus_num)
        self.bus.read_byte(self.addr)
        return True

    def runner(self):
        """Runs either interrupt-driven or polling loop."""
        self.stop_flag = False
        if self.int_pin is None:
            self.loop_polling() # Actually... it's not implemented =D
        else:
            self.loop_interrupts()

    def loop_interrupts(self):
        """Interrupt-driven loop. Currently can only use ``RPi.GPIO`` library. Stops when ``stop_flag`` is set to True."""
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(self.int_pin, GPIO.IN)
        while not self.stop_flag:
            if not self.check_connection():
                # Looping while the device is not found
                sleep(self.connection_check_sleep)
                continue
            while GPIO.input(self.int_pin) == False and self.enabled:
                logger.debug("GPIO low, reading data")
                try:
                    data = self.bus.read_byte(self.addr)
                    logger.debug("Received {:#010b}".format(data))
                except IOError:
                    if self.connected.isSet():
                        logger.error("Can't get data from keypad!")
                        self.connected.clear()
                else:
                    if not self.connected.isSet():
                        logger.info("Receiving data from keypad again!")
                        self.connected.set()
                    if data != 0:
                        data -= 1
                        if data in range(len(self.mapping)):
                            key_name = self.mapping[data]
                            logger.debug("Maps to valid key: {}".format(key_name))
                            self.map_and_send_key(key_name)
                        else:
                            logger.info("Unknown data arrived: {}".format(data))
                    else:
                        logger.warning("Received 0 from keypad though the interrupt has been triggered!")
                        sleep(0.1)
            sleep(0.1)

if __name__ == "__main__":
    id = InputDevice(addr = 0x12, int_pin = 16, threaded=False)
    id.runner()
