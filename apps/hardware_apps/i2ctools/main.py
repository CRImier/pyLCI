menu_name = "I2C tools"

from subprocess import call
from ui import Menu, Printer
from collections import OrderedDict
from time import sleep

import smbus

current_bus = None

def i2c_detect():
    global current_bus
    Printer("Scanning:", i, o, 0)
    current_bus = smbus.SMBus(1) # 1 indicates /dev/i2c-1
    found_devices = OrderedDict()
    for device in range(128):
      try: #If you try to read and it answers, it's there
         current_bus.read_byte(device)
      except IOError as e: 
         if e.errno == 16:
             found_devices[device] = "busy"
         elif e.errno == 121:
             pass
         else:
             print("Errno {} unknown - can be used? {}".format(e.errno, repr(e)))
      else:
         found_devices[device] = "ok"
    if not found_devices:
        Printer("No devices found", i, o, 2)
    else:
        data = ["{} - {}".format(hex(dev), state) for dev, state in found_devices.iteritems()]
        Printer(data, i, o, 2)

def i2c_device_menu(address):
    current_bus

#Some globals for LCS
main_menu = None
callback = None
#Some globals for us
i = None
o = None

main_menu_contents = [
["I2C detect", i2c_detect]
#["Input address", i2c_select]
]

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output
    main_menu = Menu(main_menu_contents, i, o, "I2C tools menu")
    callback = main_menu.activate

