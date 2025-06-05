menu_name = "Test hangup"

from ui import Printer
from time import sleep

i = None
o = None

def init_app(input, output):
    global i, o
    i = input
    o = output

def callback():
    Printer("Hangup", None, o, 0)
    while True:
        sleep(1)
