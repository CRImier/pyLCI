menu_name = "I2C tools"

from subprocess import call
from ui.menu import Menu

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
        o.display_data("No devices found")
        sleep(2)
    else:
        screen_rows = o.rows
        num_screens = device_count/screen_rows
        if device_count%screen_rows != 0: #There is one more screen, it's just not full but we need to add one more.
            num_screens += 1
        for screen_num in range(num_screens):
            shown_element_numbers = [(screen_num*screen_rows)+i for i in range(screen_rows)]
            screen_data = [found_devices[i] for i in shown_element_numbers] 
            o.clear()
            o.display_data(*screen_data)
            sleep(1)


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
    main_menu = Menu(main_menu_contents, o, i, "I2C tools")
    callback = main_menu.activate

