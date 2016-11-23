menu_name = "PDB console"

from ui import Printer

#Some globals for us
i = None
o = None

def callback():
    import pdb;pdb.set_trace()

def init_app(input, output):
    global callback, i, o
    i = input; o = output

