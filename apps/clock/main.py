menu_name = "Clock" 

from datetime import datetime

from ui import Refresher

def show_time():
    now = datetime.now()
    return [now.strftime("%H:%M:%S").center(o.cols), now.strftime("%Y-%m-%d").center(o.cols)]

i = None; o = None

def callback():
    Refresher(show_time, i, o, 1, name="Clock refresher").activate()

def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals


