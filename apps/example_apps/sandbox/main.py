menu_name = "Python sandbox"

from ui import Printer

#Some globals for us
i = None
o = None

def callback():
    import code
    code.interact(local=dict(globals(), **locals()))

def init_app(input, output):
    global callback, i, o
    i = input; o = output

