menu_name = "I2C tools"

from subprocess import call
from ui import Menu, Printer

from time import sleep

import smbus

def i2c_detect():
    o.clear()  #This code for printing data one element on one row begs for a separate UI element module
    o.display_data("Scanning:")
    bus = smbus.SMBus(1) # 1 indicates /dev/i2c-1
    found_devices = []
    for device in range(128):
      try: #If you try to read and it answers, it's there
         bus.read_byte(device)
      except IOError: 
         pass
      else:
         found_devices.append(str(hex(device)))
    
    device_count = len(found_devices)
    if device_count == 0:
        Printer("No devices found", i, o, 2, skippable=True)
    else:
        Printer(found_devices, i, o, 2, skippable=True)

#Some globals for LCS
main_menu = None
callback = None
#Some globals for us
i = None
o = None

main_menu_contents = [
["I2C detect", i2c_detect],
["Exit", 'exit']
]

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output
    main_menu = Menu(main_menu_contents, i, o, "I2C tools")
    callback = main_menu.activate

