menu_name = "Hello World" #ZPUI needs this variable to show app name in the main menu

from ui import PrettyPrinter #This UI element prints your text on the screen, waits the amount of time you tell it to and exits as well as splitting the text into blocks so it first the screen

#Some globals for storing input and output device objects
i = None
o = None

def callback():
    """A function that's called when the app is selected in the menu"""
    PrettyPrinter("Hello and welcome to Aperture Science computer aided enrichment center", i, o, sleep_time=5, skippable=True)

def init_app(input, output):
    """A function called once when ZPUI loads, to pass all the variables to the app"""
    global i, o
    i = input; o = output
