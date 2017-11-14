menu_name = "USB control"

from zerophone_hw import USB_DCDC
from ui import Menu, Printer
from time import sleep
import os

i = None
o = None

dcdc = USB_DCDC()

def dcdc_off_on():
    dcdc.off()
    sleep(0.5)
    dcdc.on()

usb_file = None
usb_file_base_dir = "/sys/devices/platform/soc/"
usb_control_file = "buspower"
usb_full_path = None

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
["Turn 5V DC-DC on", dcdc.on],
["Turn 5V DC-DC off", dcdc.off],
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

