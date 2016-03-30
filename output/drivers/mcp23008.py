import smbus
from time import sleep

def delay(time):
    sleep(time/1000.0)

def delayMicroseconds(time):
    sleep(time/1000000.0)

from hd44780 import HD44780

class Screen(HD44780):

    def __init__(self, rows=2, cols=16, addr=0x27, bus=1, debug=False):
        HD44780.__init__(self, rows=rows, cols=cols, debug=debug)
        self.bus_num = bus
        self.bus = smbus.SMBus(self.bus_num)
        self.addr = addr
        self.debug = debug
        self.i2c_init()
        self.init_display()
        
    def i2c_init(self):
        self.setMCPreg(0x05, 0x0c)
        self.setMCPreg(0x00, 0x00)
        """delay(20.0)
        self.write_byte(0x30)
        delay(20.0)
        self.write_byte(0x30)
        delay(20.0)
        self.write_byte(0x30)
        delay(20.0)
        self.write_byte(0x02)
        delay(20.0)
        for byte in [0x28, 0x08, 0x0c]:
            self.write_byte(byte)
        self.clear()"""

    def setMCPreg(self, reg, val):
        self.bus.write_byte_data(self.addr, reg, val)

    def write4bits(self, data, char_mode=False):
        if char_mode:
            data |= 0x10
        #if self.debug:
        #    print(hex(data))
        self.setMCPreg(0x0a, data)
        data ^= 0x80
        delayMicroseconds(1.0)
        self.setMCPreg(0x0a, data)
        data ^= 0x80
        delayMicroseconds(1.0)
        self.setMCPreg(0x0a, data)
        delay(1.0)
        

if __name__ == "__main__":
    screen = Screen(bus=1, addr=0x27, cols=16, rows=2, debug=True)
    print("Initialising with HD44780:")
    line = "0123456789012345"
    if True:
        screen.display_data(line, line[::-1])
        sleep(1)
        screen.display_data(line[::-1], line)
        sleep(1)
        screen.clear()
