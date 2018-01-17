menu_name = "ZeroMenu"

from apps.flashlight import main as flashlight
from zerophone_hw import USB_DCDC
from datetime import datetime
from threading import Event
from ui import Menu, PrettyPrinter
import os
i = None; o = None

previous_image = None
zeromenu = None
zeromenu_running = Event()

dcdc = USB_DCDC()

def take_screenshot():
    if previous_image != None:
        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        filename = "screenshot_{}.png".format(timestamp)
        path = os.path.join("screenshots/", filename)
        previous_image.save(path, "PNG")
        PrettyPrinter("Screenshot saved to {}".format(path), i, o)

def toggle_flashlight():
    flashlight.callback()

def usb_on():
    dcdc.on()

def usb_off():
    dcdc.off()

menu_contents = [["Flashlight", toggle_flashlight],
                 ["USB on", usb_on],
                 ["USB off", usb_off],
                 ["Take screenshot", take_screenshot] ]

def call_menu():
    global previous_image
    #Dirty hack - making an experimental function work before there are facilities for it
    if zeromenu_running.isSet():
        zeromenu.deactivate()
        return
    zeromenu_running.set()
    #Saving currently displayed image
    previous_image = o.current_image
    #Stealing the display_image function and replacing it with a stub
    #!!!Doesn't actually work!!!
    #orig_display_image_func = o.display_image
    #def fake_display_image_func(image):
    #    previous_image = image
    #o.display_image = fake_display_image_func
    #Saving the keymap
    previous_keymap = i.get_keymap()
    #Running the menu
    zeromenu.activate()
    #Menu exited
    #Returning the function back to where it belongs
    #o.display_image = orig_display_image_func
    o.display_image(previous_image)
    #Setting the keymap back
    i.set_keymap(previous_keymap)
    #All done, clearnign flags and exiting
    zeromenu_running.clear()

def init_app(input, output):
    global i, o, zeromenu
    i = input; o = output
    #i.set_maskable_callback("KEY_PROG2", call_menu)
    zeromenu = Menu(menu_contents, i, o, name="ZeroMenu main menu")

#callback = call_menu #If uncommented, ZeroMenu will show up in main menu
