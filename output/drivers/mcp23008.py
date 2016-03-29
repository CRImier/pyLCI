import smbus
from time import sleep

def delay(time):
    sleep(time/1000.0)

def delayMicroseconds(time):
    sleep(time/1000000.0)


class Screen():
    data_mask = 0x00

    def __init__(self, rows=2, cols=16, addr=0x27):
        self.rows = rows
        self.cols = cols
        self.bus = smbus.SMBus(1)
        self.addr = addr
        self.i2c_init()
        
    def setMCPreg(self, reg, val):
        self.bus.write_byte_data(self.addr, reg, val)

    def send2LCD(self, data):
        data |= self.data_mask
        self.setMCPreg(0x0a, data)
        data ^= 0x80
        delayMicroseconds(1.0)
        self.setMCPreg(0x0a, data)
        data ^= 0x80
        delayMicroseconds(1.0)
        self.setMCPreg(0x0a, data)
        delay(1.0)
        
    def writeLCDbyte(self, data):
        self.send2LCD(data >> 4)
        self.send2LCD(data & 0x0F)

    def i2c_init(self):
        self.setMCPreg(0x05, 0x0c)
        self.setMCPreg(0x00, 0x00)
        delay(20.0)
        self.send2LCD(0x03)
        delay(2.0)
        self.send2LCD(0x03)
        delayMicroseconds(100.0)
        self.send2LCD(0x03)
        delay(2.0)
        self.send2LCD(0x02)
        for byte in [0x28, 0x08, 0x0c]:
            self.writeLCDbyte(byte)
        delayMicroseconds(30.0)
        self.writeLCDbyte(0x01)
        delay(3)

    def i2c_write(self, value):
        self.bus.write_byte_data(self.addr, 0, value) 

    def cursorTo(self, row, col):
        offsets = [0x00, 0x40, 0x14, 0x54]
        self.write_command(0x80|(col+offsets[row]))

    def write_command(self, command):
        self.writeLCDbyte(command)
        delayMicroseconds(50.0)

    def print_char(self, char):
        self.data_mask |= 0x10
        self.writeLCDbyte(ord(char))
        self.data_mask ^= 0x10

    def println(self, line):
        for char in line:
            self.print_char(char)

    def clear(self):
        self.write_command(0x01)

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
