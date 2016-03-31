import smbus
from time import sleep

from hd44780 import HD44780

def delay(time):
    sleep(time/1000.0)

def delayMicroseconds(time):
    sleep(time/1000000.0)


class Screen(HD44780):

    enable_mask = 1<<2
    #rw_mask = 1<<1
    rs_mask = 1<<0
    backlight_mask = 1<<3

    data_mask = 0x00

    def __init__(self, **kwargs):
        self.bus_num = kwargs.pop("bus", 1)
        self.bus = smbus.SMBus(self.bus_num)
        self.addr = kwargs.pop("addr", 0x27)
        self.debug = kwargs.pop("debug", False)
        rows = kwargs.pop("rows", 2)
        cols = kwargs.pop("cols", 16)
        HD44780.__init__(self, rows = rows, cols = cols, debug = self.debug)
        self.init_display(**kwargs)
        self.enable_backlight()
        
    def enable_backlight(self):
        self.data_mask = self.data_mask|self.backlight_mask
        
    def disable_backlight(self):
        self.data_mask = self.data_mask& ~self.backlight_mask
       
    def write_byte(self, data, char_mode = False):
        if self.debug and not char_mode:
            print(hex(data))
        self.write4bits((data & 0xF0), char_mode)
        self.write4bits((data << 4), char_mode)

    def write4bits(self, value, char_mode = False):
        if char_mode:
            value = value |self.rs_mask
        value = value & ~ self.enable_mask
        self.expanderWrite(value)
        self.expanderWrite(value | self.enable_mask)
        self.expanderWrite(value)        

    def expanderWrite(self, data):
        self.bus.write_byte_data(self.addr, 0, data|self.data_mask)
       

if __name__ == "__main__":
    screen = Screen(bus=1, addr=0x26, cols=16, rows=2, autoscroll=False)
    line = "01234567890123456789"
    while True:
        screen.display_data(line, line[::-1])
        sleep(1)      
        screen.display_data(line[::-1], line)
        sleep(1)      



