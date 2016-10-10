menu_name = "FFS test app"

from ui import Printer, format_for_screen as ffs

from subprocess import check_output

callback = None
#Some globals for us
i = None
o = None

def init_app(input, output):
    global callback, i, o
    i = input; o = output
    lsusb_output = check_output(['lsusb'])
    callback = lambda: Printer(ffs(lsusb_output, o.cols), i, o, sleep_time=5, skippable=True)

