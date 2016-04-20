"""
    print(cpu_info())
{'CPU implementer': '0x41', 'Features': 'half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm crc32', 'CPU architecture': '7', 'BogoMIPS': '76.80', 'Hardware': 'BCM2709', 'CPU revision': '4', 'CPU part': '0xd03', 'model name': 'ARMv7 Processor rev 4 (v7l)', 'Serial': '00000000f6570ff1', 'processor': '3', 'CPU variant': '0x0', 'Revision': 'a02082'}
    print(is_raspberry_pi())
True
    print(free())
{'UsedBC': 203, 'Used': 672, 'SwapTotal': 99, 'Cached': 431, 'SwapFree': 99, 'Free': 253, 'FreeBC': 722, 'SwapUsed': 0, 'Shared': 17, 'Total': 925, 'Buffers': 38}
    print(linux_info())
(0.0, 0.01, 0.05)
"""

menu_name = "System info"

from subprocess import call
from ui import Menu, Printer

import sys_info

def show_uptime_load():
    loadavg_string = " ".join([str(number) for number in sys_info.loadavg()])
    uptime_string = sys_info.uptime()
    Printer([uptime_string, loadavg_string], i, o, skippable=True)

def show_memory():
    memory_info = sys_info.free()
    menu_contents = [
    ["Free {}MB".format(memory_info["Free"])],
    ["Used {}MB".format(memory_info["Used"])],
    ["FreeBC {}MB".format(memory_info["FreeBC"])],
    ["UsedBC {}MB".format(memory_info["UsedBC"])],
    ["Total {}MB".format(memory_info["Total"])],
    ["Swap {}MB".format(memory_info["SwapTotal"])],
    ["SwapUsed {}MB".format(memory_info["SwapUsed"])],
    ["SwapFree {}MB".format(memory_info["SwapFree"])],
    ["Cached {}MB".format(memory_info["Cached"])],
    ["Shared {}MB".format(memory_info["Shared"])],
    ["Buffers {}MB".format(memory_info["Buffers"])]]
    Menu(menu_contents, i, o).activate()

def show_linux_info():
    linux_info = sys_info.linux_info()
    menu_contents = [
    [["Hostname:", linux_info["hostname"]]],
    [["Kernel version:", linux_info["k_release"]]],
    [["Architecture:", linux_info["machine"]]],
    [["Distribution:", " ".join(linux_info["distribution"])]]
    ]
    Menu(menu_contents, i, o, entry_height=2).activate()

#Some globals for pyLCI
callback = None
#Some globals for us
i = None
o = None


def init_app(input, output):
    global callback, i, o
    i = input; o = output

    menu_contents = [
    ["Uptime&load", show_uptime_load],
    #["CPU", show_cpu],
    ["Memory", show_memory],
    ["Linux info", show_linux_info]
    #["Processes", show_processes]
    ]

    #if detect_raspberry:
    #    menu.contents.append("Raspberry Pi", rpi_menu)
    main_menu = Menu(menu_contents, i, o, "System menu")
    callback = main_menu.activate

