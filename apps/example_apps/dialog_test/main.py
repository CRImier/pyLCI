menu_name = "DialogBox test" #App name as seen in main menu while using the system

from ui import DialogBox

#Some globals for us
i = None #Input device
o = None #Output device

def callback():
    print(DialogBox('ync', i, o, message="Test test test").activate())

def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals

