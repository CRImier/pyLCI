menu_name = "Checkbox test"

from subprocess import call
from ui import Checkbox


#Some globals for pyLCI
callback = None
#Some globals for us
i = None
o = None

checkbox_contents = [
["First element", '1_el', False],
["Second element", '2_el', True],
["Third element", '3_el', False],
["Fourth element xD", '4_el', True]
]

def init_app(input, output):
    global callback, i, o
    i = input; o = output
    def callback():
        print(Checkbox(checkbox_contents, i, o, "Shutdown menu").activate())

