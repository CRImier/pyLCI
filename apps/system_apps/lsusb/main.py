menu_name = "USB devices"

from ui import Menu, Printer, ellipsize

import lsusb

def show_devices():
    menu_contents = []
    try:
        usb_devices = lsusb.lsusb()
    except OSError:
        Printer(["Do you have", "lsusb?"], i, o, 2)
        return False
    for bus, dev, vid_pid, name in usb_devices:   
        ell_name = ellipsize(name, o.cols)
        menu_contents.append([["{}{},{}".format(bus, dev, vid_pid), ell_name], lambda x=name: Printer(x, i, o, skippable=True)])
    Menu(menu_contents, i, o, entry_height=2).activate()

#Some globals for pyLCI
callback = show_devices
#Some globals for us
i = None
o = None


def init_app(input, output):
    global i, o
    i = input; o = output

