menu_name = "ZeroMenu"

from apps.flashlight import main as flashlight
from zerophone_hw import USB_DCDC
from datetime import datetime
from threading import Event
from ui import Menu, PrettyPrinter
import os
i = None; o = None

context = None
zeromenu = None

dcdc = USB_DCDC()

def take_screenshot():
    image = context.get_previous_context_image()
    if image != None:
        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        filename = "screenshot_{}.png".format(timestamp)
        path = os.path.join("screenshots/", filename)
        image.save(path, "PNG")
        PrettyPrinter("Screenshot saved to {}".format(path), i, o)

def toggle_flashlight():
    flashlight.callback()

def usb_on():
    dcdc.on()

def usb_off():
    dcdc.off()

def set_context(received_context):
    global context
    context = received_context
    context.request_global_keymap({"KEY_PROG2":context.request_switch})
    context.set_target(zeromenu.activate)

def init_app(input, output):
    global i, o, zeromenu
    i = input; o = output
    menu_contents = [["Flashlight", toggle_flashlight],
                     ["USB on", usb_on],
                     ["USB off", usb_off],
                     ["Take screenshot", take_screenshot] ]
    zeromenu = Menu(menu_contents, i, o, name="ZeroMenu main menu")

