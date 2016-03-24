import pifacecad

class Screen():
    type = "char"

    def __init__(self, rows=2, cols=16):
        self.rows = rows
        self.cols = cols
        self.lcd = pifacecad.PiFaceCAD().lcd
        self.backlight = True

    def enable_backlight(self): 
        #A complicated flag system is necessary because otherwise it conflicts with the later registered pifacecad input device
        self.backlight = True

    def disable_backlight(self):
        self.backlight = False

    def clear(self):
        self.lcd.clear()

    def display_data(self, *args):
        if self.backlight:
            self.lcd.backlight_on() 
        else:
            self.lcd.backlight_off() 
        self.lcd.clear()
        for arg in args:
            arg = arg[:self.cols].ljust(self.cols)
        self.lcd.write('\n'.join(args))
