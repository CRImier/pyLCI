menu_name = "Number input app" 

from datetime import datetime

from ui import IntegerInDecrementInput as Input

#Some globals for us
i = None #Input device
o = None #Output device

#Callback for pyLCI. It gets called when application is activated in the main menu
def callback():
    number_input = Input(0, i, o)
    print(number_input.activate())

def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals

