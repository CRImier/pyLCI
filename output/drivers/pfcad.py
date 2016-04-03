import pifacecad
from time import sleep

class Screen():
    type = "char"

    def __init__(self, rows=2, cols=16):
        self.rows = rows
        self.cols = cols
        self.lcd = pifacecad.PiFaceCAD().lcd
        self.backlight = True
        self.busy_flag = False

    def enable_backlight(self): 
        #A complicated flag system is necessary because otherwise it conflicts with the later registered pifacecad input device
        self.backlight = True

    def disable_backlight(self):
        self.backlight = False
        self.lcd.backlight_off()

    def clear(self):
        self.lcd.clear()

    def display_data(self, *args):
        while self.busy_flag:
            sleep(0.01)
        self.lcd.blink_off()
        self.lcd.cursor_off()
        if self.backlight:
            self.lcd.backlight_on() 
        self.busy_flag = False
        self.lcd.clear()
        for arg in args:
            arg = arg[:self.cols].ljust(self.cols)
        self.lcd.write('\n'.join(args))
        self.busy_flag = False
