menu_name = "Test app"

from ui import Printer

#Some globals for LCS
callback = None
#Some globals for us
i = None
o = None

def init_app(input, output):
    global callback, i, o
    i = input; o = output
    callback = lambda: Printer(["Hello and", "welcome to", "Aperture Science", "computer aided", "enrichment", "center"], i, o, sleep_time=5, skippable=True)

