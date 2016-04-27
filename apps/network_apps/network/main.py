menu_name = "Interfaces"
#Some globals for LCS
callback = None
#Some globals for us
if_menu = None
i = None
o = None

from subprocess import call
from time import sleep

from ui import Menu, Printer
from if_info import parse_ip_addr

def show_ifc_data(ifc_name, ifc_data):
    ip, mask = str(ifc_data['addr']).rsplit('/', 1)
    ip_header = "IP: "
    mask_str = "/{}".format(mask)
    ip_header_str = ip_header + mask_str.rjust(o.cols-len(ip_header)) #Magic to make it beautiful
    print(ip_header_str)
    ifd_menu_contents = [
    ["state: "+str(ifc_data['state'])],
    [[ip_header_str, ip]],
    ["IP6: "+str(ifc_data['addr6']), lambda: Printer(str(ifc_data['addr6']), i, o, 3)],
    ["MAC: "+str(ifc_data['ph_addr'])]
    ]
    ifd_menu = Menu(ifd_menu_contents, i, o, "{} interface data menu".format(ifc_name), entry_height=2)
    ifd_menu.activate()

def update_if_menu_contents():
    #This function builds a menu out of all the interface names, each having a callback to show_if_function with interface name as argument
    global if_menu
    menu_contents = []
    ifc_dict = parse_ip_addr()
    for ifc in ifc_dict:
        ifc_data = ifc_dict[ifc]
        menu_contents.append([ifc, lambda x=ifc, y=ifc_data: show_ifc_data(x, y)])
    menu_contents.append(["Exit", 'exit'])
    if_menu.set_contents(menu_contents)

def activate_wrapper(activate_cb):
    def wrapper():
        update_if_menu_contents()
        activate_cb()
    return wrapper

def init_app(input, output):
    global if_menu, callback, i, o
    i = input; o = output
    if_menu = Menu([], i, o, "Interface selection menu")
    if_menu.activate = activate_wrapper(if_menu.activate) #Decorating around the menu.activate module so that every time menu is activated interface data is refreshed
    callback = if_menu.activate
    


"""
def i2c_detect():
    o.clear()  #This code for printing data one element on one row begs for a separate UI element module
    o.display_data("Scanning:")
    bus = smbus.SMBus(1) # 1 indicates /dev/i2c-1
    found_devices = []
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
"""

