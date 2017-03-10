menu_name = "Phone" 

from ui import Refresher
from ui.experimental import NumberKeypadInputLayer

from phone import modem, ATError

def nocarrier()

def calling_status():

def call(number):
    Ref
    print("Calling {}".format(number))
 
callback = None
i = None 
o = None 

def init_app(input, output):
    global callback, i, o
    i = input; o = output 
    keymap = {"KEY_ANSWER":[call]}
    phone_layer = NumberKeypadInputLayer(i, o, "Call number", keymap, name="Phone call layer")
    callback = phone_layer.activate

