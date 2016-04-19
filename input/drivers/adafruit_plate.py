import smbus
from time import sleep
import threading

class InputDevice():
    """A driver for Adafruit-developed Raspberry Pi character LCD&button shields based on MCP23017, either Adafruit-made or Chinese-made.
 
       Tested on hardware compatible with Adafruit schematic and working with Adafruit libraries, but not on genuine Adafruit hardware. 
    """
    mapping = [
    "KEY_KPENTER",
    "KEY_RIGHT",
    "KEY_DOWN",
    "KEY_UP",
    "KEY_LEFT"]
    stop_flag = False
    previous_data = 0

    def __init__(self, addr = 0x20, bus = 1):
        """Initialises the ``InputDevice`` object.  
                                                                               
        Kwargs:                                                                  
                                                                                 
            * ``bus``: I2C bus number.
            * ``addr``: I2C address of the expander.

        """
        self.bus_num = bus
        self.bus = smbus.SMBus(self.bus_num)
        if type(addr) in [str, unicode]:
            addr = int(addr, 16)
        self.addr = addr

    def start(self):
        """Starts listening on the input device. Also, initialises the IO expander."""
        self.stop_flag = False
        self.setMCPreg(0x00, 0x1F)
        self.setMCPreg(0x0C, 0x1F)
        self.loop_polling()

    def loop_polling(self):
        """Polling loop. Stops when ``stop_flag`` is set to True."""
        button_states = []
        while not self.stop_flag:
            data = (~self.readMCPreg(0x12)&0x1F)
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
        """A hook to be overridden by ``InputListener``. Otherwise, prints out key names as soon as they're released so is useful for debugging."""
        print(key)

    def activate(self):
        """Starts a thread with ``start`` function as target."""
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()

    def setMCPreg(self, reg, val):
        """Sets the MCP23017 register."""
        self.bus.write_byte_data(self.addr, reg, val)

    def readMCPreg(self, reg):
        """Reads the MCP23017 register."""
        return self.bus.read_byte_data(self.addr, reg)


if __name__ == "__main__":
    id = InputDevice(addr = 0x20)
    id.start()
