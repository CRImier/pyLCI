import smbus
from time import sleep

def delay(time):
    sleep(time/1000.0)

def delayMicroseconds(time):
    sleep(time/1000000.0)

from hd44780 import HD44780

class Screen(HD44780):

    def __init__(self, **kwargs):
        self.bus_num = kwargs.pop("bus", 1)
        self.bus = smbus.SMBus(self.bus_num)
        self.addr = kwargs.pop("addr", 0x27)
        self.debug = kwargs.pop("debug", False)
        rows = kwargs.pop("rows", 2)
        cols = kwargs.pop("cols", 16)
        HD44780.__init__(self, rows = rows, cols = cols, debug = self.debug)
        self.i2c_init()
        self.init_display(**kwargs)
        
    def i2c_init(self):
        self.setMCPreg(0x05, 0x0c)
        self.setMCPreg(0x00, 0x00)

    def setMCPreg(self, reg, val):
        self.bus.write_byte_data(self.addr, reg, val)

    def write_byte(self, byte, char_mode=False):
        if self.debug and not char_mode:        
            print(hex(byte))                    
        self.write4bits(byte >> 4, char_mode)   
        self.write4bits(byte & 0x0F, char_mode) 

    def write4bits(self, data, char_mode=False):
        if char_mode:
            data |= 0x10
        self.setMCPreg(0x0a, data)
        data ^= 0x80
        delayMicroseconds(1.0)
        self.setMCPreg(0x0a, data)
        data ^= 0x80
        delayMicroseconds(1.0)
        self.setMCPreg(0x0a, data)
        delay(1.0)
        

if __name__ == "__main__":
    screen = Screen(bus=1, addr=0x27, cols=16, rows=2, debug=True, autoscroll=False)
    line = "0123456789012345"
    if True:
        screen.display_data(line, line[::-1])
        sleep(1)
        screen.display_data(line[::-1], line)
        sleep(1)
        screen.clear()
