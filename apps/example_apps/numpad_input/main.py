menu_name = "Char input app" 

from ui import NumpadCharInput as CharInput, NumpadNumberInput as NumberInput

#Some globals for us
i = None #Input device
o = None #Output device

#Callback for ZPUI. It gets called when application is activated in the main menu
def callback():
    char_input = CharInput(i, o, message="Input characters")
    print(repr(char_input.activate()))
    number_input = NumberInput(i, o, message="Input numbers")
    print(repr(number_input.activate()))

def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals

