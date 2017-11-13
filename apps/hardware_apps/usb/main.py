menu_name = "USB control"

from ui import Menu, Printer
from time import sleep
import os

import sys
import gpio
sys.excepthook = sys.__excepthook__
#GPIO library workaround - it sets excepthook
#to PDB debug, that's good but it's going to
#propagate through ZPUI code, and that's not desirable
gpio.log.setLevel(gpio.logging.INFO)
#Otherwise, a bunch of stuff is printed in the terminal

#TODO - move DC-DC-specific part into zerophone_hw package

i = None
o = None

dcdc_gpio = 510
#It doesn't make sense to export the DC-DC GPIO as the app is initialized, 
#so that the current state of GPIO is saved even if ZPUI restarts
dcdc_exported = False

usb_file = None
usb_file_base_dir = "/sys/devices/platform/soc/"
usb_control_file = "buspower"
usb_full_path = None

def dcdc_off_on():
    global dcdc_exported
    if not dcdc_exported:
        #DC-DC GPIO not yet set up
        gpio.setup(dcdc_gpio, gpio.OUT)
        dcdc_exported = True
    gpio.set(dcdc_gpio, True)
    sleep(0.5)
    gpio.set(dcdc_gpio, False)

def dcdc_on():
    global dcdc_exported
    if not dcdc_exported:
        gpio.setup(dcdc_gpio, gpio.OUT)
        dcdc_exported = True
    gpio.set(dcdc_gpio, False)

def dcdc_off():
    global dcdc_exported
    if not dcdc_exported:
        gpio.setup(dcdc_gpio, gpio.OUT)
        dcdc_exported = True
    gpio.set(dcdc_gpio, True)

def usb_off_on():
    with open(usb_full_path, "w") as f:
        f.write("0")
        sleep(0.5)
        f.write("1")

def usb_on():
    with open(usb_full_path, "w") as f:
        f.write("1")

def usb_off():
    with open(usb_full_path, "w") as f:
        f.write("0")


main_menu_contents = [ 
["Restart 5V DC-DC", dcdc_off_on],
["Turn 5V DC-DC on", dcdc_on],
["Turn 5V DC-DC off", dcdc_off],
["Restart USB bus", usb_off_on],
["Turn USB bus on", usb_on],
["Turn USB bus off", usb_off]
]

def init_app(input, output):
    global i, o, usb_file, usb_full_path
    i = input; o = output
    #Find the usb device control directory
    device_files = os.listdir(usb_file_base_dir)
    usb_files = [file for file in device_files if file.endswith(".usb")]
    if not usb_files:
        print("Can't find suitable USB file at {}! What's wrong with this hardware?".format(usb_file_base_dir))
        raise IOError
    usb_file = usb_files[0] #I'm guessing having more than one file would mean 
    #having more than one USB controller, so this is not Raspberry Pi stuff anymore
    #and I can only test this on a Pi right now.
    usb_full_path = os.path.join(usb_file_base_dir, usb_file, usb_control_file)
    if not os.path.exists(usb_full_path):
        print("Can't find {} file at {}! What's wrong with this hardware?".format(usb_control_file, usb_full_path))
        raise IOError
        
def callback():
    Menu(main_menu_contents, i, o, "USB app menu").activate()

