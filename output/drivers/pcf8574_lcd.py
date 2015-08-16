import smbus
from time import sleep

from output.output import BaseScreen

def delay(time):
    sleep(time/1000.0)

def delayMicroseconds(time):
    sleep(time/1000000.0)


class Screen(BaseScreen):

    enable_mask = 0x04
    rw_mask = 0x02
    rs_mask = 0x01
    backlight_mask = 0x08

    data_mask = 0x00

    def __init__(self, rows=2, cols=16, addr=0x27):
        self.rows = rows
        self.cols = cols
        self.bus = smbus.SMBus(1)
        self.addr = addr
        self.i2c_init()
        
    def i2c_init(self):
        delayMicroseconds(50.0)
        self.expanderWrite(self.backlight_mask)
        delay(1.0)
        self.write4bits(0x30)
        delay(4.5)
        self.write4bits(0x30)
        delay(4.5)
        self.write4bits(0x30)
        delay(0.15)
        self.write4bits(0x20)
        self.command(0x20|0x08)
        self.command(0x04|0x08)
        delayMicroseconds(30.0)
        self.clear()
        self.command(0x04|0x02)
        delay(3)

    def command(self, value):
        self.send(value, 0)
        delayMicroseconds(50.0)

    def write(self, value):
        self.send(value, self.rs_mask)

    def pulseEnable(self, data):
        self.expanderWrite(data | self.enable_mask)
        delayMicroseconds(1)
        self.expanderWrite(data & ~self.enable_mask)
        delayMicroseconds(1)
        
    def send(self, data, mode):
        self.write4bits((data & 0xF0)|mode)
        self.write4bits((data << 4)|mode)

    def write4bits(self, value):
        self.expanderWrite(value)
        self.pulseEnable(value)        

    def expanderWrite(self, data):
        self.bus.write_byte_data(self.addr, 0, data|self.backlight_mask) 

    def cursorTo(self, row, col):
        offsets = [0x00, 0x40, 0x14, 0x54]
        self.command(0x80|(offsets[row]+col))

    def print_char(self, char):
        self.write(ord(char))

    def println(self, line):
        for char in line:
            self.print_char(char)

    def clear(self):
        self.command(0x10)

    def display_data(self, *args):
        self.clear()
        for line, arg in enumerate(args):
            self.cursorTo(line, 0)
            self.println(arg[:self.cols].ljust(self.cols))
       

if __name__ == "__main__":
    screen = Screen()
    line = "0123456789012345"
    while True:
        screen.cursorTo(0, 0)
        screen.println(line)
        screen.cursorTo(1, 0)
        screen.println(line)
        sleep(1)      
        screen.cursorTo(0, 0)
        screen.println(line[::-1])
        screen.cursorTo(1, 0)
        screen.println(line[::-1])
        sleep(1)      
