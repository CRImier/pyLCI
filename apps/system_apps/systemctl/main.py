menu_name = "Systemctl"

config_filename = "config.json" 
default_config = '{"allowed_types":["service","target"], "pinned_units":["pylci.service"]}'

callback = None

main_menu = None
i = None
o = None

from time import sleep

from helpers import read_config, write_config
from ui import Menu, Printer, Checkbox, MenuExitException

import systemctl

import os,sys
current_module_path = os.path.dirname(sys.modules[__name__].__file__)

config_path = os.path.join(current_module_path, config_filename)

try:
    config = read_config(config_path)
    if "pinned_values" not in config:
        config["pinned_values"] = []
        write_config(config, config_path)
except (ValueError, IOError):
    print("Systemctl app: broken config, restoring with defaults...")
    with open(config_path, "w") as f:
        f.write(default_config)
    config = read_config(config_path)

def change_filters():
    global config
    all_types = [
    ["Slices", 'slice'],
    ["Sockets", 'socket'],
    ["Services", 'service'],
    ["Automounts", 'automount'],
    ["Mounts", 'mount'],
    ["Timers", 'timer'],
    ["Paths", 'path'],
    ["Devices", 'device'],
    ["Scopes", 'scope'],
    ["Targets", 'target']]
    checkbox_contents = []
    for type in all_types:
        checkbox_contents.append([type[0], type[1], type[1] in config["allowed_types"]])
    states = Checkbox(checkbox_contents, i, o).activate()
    config["allowed_types"] = [state for state in states if states[state]] 
    write_config(config, config_path)
    
def all_units():
    menu_contents = []
    units = systemctl.list_units()
    for unit in units: 
        menu_contents.append([unit["basename"], lambda x=unit["name"]: unit_menu(x)])
    Menu(menu_contents, i, o, "All unit list menu").activate()

def pinned_units():
    menu_contents = []
    units = systemctl.list_units()
    for unit_name in config["pinned_units"]:
        menu_contents.append([unit_name, lambda x=unit_name: unit_menu(x)])
    Menu(menu_contents, i, o, "Pinned unit list menu").activate()

def filtered_units():
    menu_contents = []
    units = systemctl.list_units()
    for unit in units: 
        if unit["type"] in config["allowed_types"]:
            menu_contents.append([unit["basename"], lambda x=unit["name"]: unit_menu(x)])
    Menu(menu_contents, i, o, "All unit list menu").activate()

def unit_menu(name):
    unit_menu_contents = [
    ["Full name", lambda x=name: Printer(x, i, o)],
    ["Start unit", lambda x=name: start_unit(x)],
    ["Stop unit", lambda x=name: stop_unit(x)],
    ["Restart unit", lambda x=name: restart_unit(x)],
    ["Reload unit", lambda x=name: reload_unit(x)],
    ["Enable unit", lambda x=name: enable_unit(x)],
    ["Disable unit", lambda x=name: disable_unit(x)],
    ["Pin unit", lambda x=name: pin_unit(x)]]
    Menu(unit_menu_contents, i, o, "{} unit menu".format(name)).activate()

def pin_unit(name):
    global config
    config["pinned_units"].append(name)
    write_config(config, config_path)
    Printer(["Pinned unit", name], i, o, 1)

def start_unit(name):
    status = systemctl.action_unit("start", name)
    if status:
        Printer(["Started unit", name], i, o, 1)
    else:
        Printer(["Can't start", name], i, o, 1)
    raise MenuExitException

def stop_unit(name):
    status = systemctl.action_unit("stop", name)
    if status:
        Printer(["Stopped unit", name], i, o, 1)
    else:
        Printer(["Can't stop", name], i, o, 1)
    raise MenuExitException

def restart_unit(name):
    status = systemctl.action_unit("restart", name)
    if status:
        Printer(["Restarted unit", name], i, o, 1)
    else:
        Printer(["Can't restart", name], i, o, 1)
    raise MenuExitException

def reload_unit(name):
    status = systemctl.action_unit("reload", name)
    if status:
        Printer(["Reloaded unit", name], i, o, 1)
    else:
        Printer(["Can't reload", name], i, o, 1)
    raise MenuExitException

def enable_unit(name):
    status = systemctl.action_unit("enable", name)
    if status:
        Printer(["Enabled unit", name], i, o, 1)
    else:
        Printer(["Can't enable", name], i, o, 1)
    raise MenuExitException

def disable_unit(name):
    status = systemctl.action_unit("disable", name)
    if status:
        Printer(["Disabled unit", name], i, o, 1)
    else:
        Printer(["Can't disable", name], i, o, 1)
    raise MenuExitException

def launch():
    try:
       systemctl.list_units()
    except OSError as e:
       if e.errno == 2:
           Printer(["Do you use", "systemctl?"], i, o, 3, skippable=True)
           return
       else:
           raise e
    main_menu_contents = [
    ["Pinned units", pinned_units],
    ["Units (filtered)", filtered_units],
    ["All units", all_units],
    ["Change filters", change_filters]]
    main_menu = Menu(main_menu_contents, i, o, "systemctl main menu")
    main_menu.activate()


def init_app(input, output):
    global callback, main_menu, i, o
    i = input; o = output
    callback = launch
