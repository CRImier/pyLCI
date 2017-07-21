#Code taken from here: https://habrahabr.ru/post/332812/ and, consequently, from here: https://www.electricmonk.nl/log/2016/07/05/exploring-upnp-with-python/
menu_name = "UPnP/SSDP scan"

from ui import Menu, Printer, IntegerAdjustInput, format_for_screen as ffs
from helpers.config_parse import read_config, write_config

from collections import OrderedDict
from traceback import format_exc
from time import sleep
import socket
import sys
import os

#Some globals for us
i = None
o = None

current_module_path = os.path.dirname(sys.modules[__name__].__file__)
config_filename = "config.json"
default_config = '{"timeout":1,"dst":"239.255.255.250","st":"upnp:rootdevice"}'
config_path = os.path.join(current_module_path, config_filename)
try:
    config = read_config(config_path)
except (ValueError, IOError):
    print("{}: broken/nonexistent config, restoring with defaults...".format(menu_name))
    with open(config_path, "w") as f:
        f.write(default_config)
    config = read_config(config_path)

def run_scan():
    Printer("Scanning:", i, o, 0)
    msg = [
        'M-SEARCH * HTTP/1.1',
        'Host:{}:1900'.format(config["dst"]),
        'ST:{}'.format(config["st"]),
        'Man:"ssdp:discover"',
        'MX:1',
        '']
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(config["timeout"])
    s.sendto('\r\n'.join(msg), (config["dst"], 1900) )

    found_devices = OrderedDict()
    while True:
        try:
            data, addr = s.recvfrom(32*1024)
        except socket.timeout:
            break
        except:
            print(format_exc())
        else:
            ip_str = "{}:{}".format(*addr)
            found_devices[ip_str] = data
    
    if not found_devices:
        Printer("No devices found", i, o, 2)
    else:
        data = [[ip, lambda x=ip, y=d: read_info(x, y)] for ip, d in found_devices.iteritems()]
        Menu(data, i, o).activate()

def read_info(ip_str, data):
    print("[+] {}\n{}".format(ip_str, data))
    Printer(ffs("[+] {}\n{}".format(ip_str, data), o.cols), i, o, 5)

def adjust_timeout():
    global config
    timeout = IntegerAdjustInput(config["timeout"], i, o, message="Socket timeout:").activate()
    if timeout is not None and timeout > 0:
        config["timeout"] = timeout
        write_config(config, config_path)
    elif not timeout > 0:
        Printer(ffs("Timeout has to be larger than 0!", o.cols), i, o)

main_menu_contents = [
["Scan", run_scan],
["Change timeout", adjust_timeout]
]

def init_app(input, output):
    global i, o
    i = input; o = output

def callback():
    Menu(main_menu_contents, i, o, "I2C tools menu").activate()

