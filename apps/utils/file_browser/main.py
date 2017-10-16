menu_name = "File browser" 

from ui import PathPicker, Printer
import os

#Callback global for pyLCI. It gets called when application is activated in the main menu
callback = None

#Some globals for us
i = None #Input device
o = None #Output device

def init_app(input, output):
    global callback, i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals
    callback = browse

def print_path(path):
    if os.path.isdir(path):
        Printer("Dir: {}".format(path), i, o, 5)
    elif os.path.isfile(path):
        Printer("File: {}".format(path), i, o, 5)
    else:
        Printer("WTF: {}".format(path), i, o, 5) # ;-P

def browse():
    path_picker = PathPicker("/", i, o, callback=)
    path_picker.activate() #Menu yet to be added
