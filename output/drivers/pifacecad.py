import pifacecad

class Screen():
    type = "char"

    def __init__(self, rows=2, cols=16):
        self.rows = rows
        self.cols = cols
        self.lcd = pifacecad.PiFaceCAD().lcd


    def display_data(self, *args):
        self.lcd.backlight_on() #Had to move it here instead of __init__ because it interferes with piface2uinput... 
        self.lcd.clear()
        for arg in args:
            arg = arg[:self.cols].ljust(self.cols)
        self.lcd.write('\n'.join(args))
