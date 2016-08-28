menu_name = "Char input app" 

from ui import CharArrowKeysInput as Input

#Some globals for us
i = None #Input device
o = None #Output device

#Callback for pyLCI. It gets called when application is activated in the main menu
def callback():
    char_input = Input(i, o, initial_value = "password")
    print(char_input.activate())

def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals

