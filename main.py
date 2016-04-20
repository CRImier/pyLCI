#!/usr/bin/env python
import sys
import os
#Welcome to pyLCI innards
#Here, things are about i and o, which are input and output
#And we output things for debugging, so o goes first.
from output import output

#These lines are here so that welcome message stays on the screen a little longer:
output.init()
o = output.screen
from ui import Printer
Printer(["Welcome to", "pyLCI"], None, o, 0)

try:
    #All the LCI-related modules are imported here
    from input import input
    from ui import Menu
    #Now we init the input subsystem.
    input.init()
    i = input.listener
except:
    Printer(["Oops. :(", "y u make mistake"], None, o, 0) #Yeah, that's about all the debug data. 
    #import time;time.sleep(3) #u make mi sad i go to slip
    #o.clear()
    raise

#Here go all native Python modules. It's close to impossible to screw that up.
from subprocess import call
from time import sleep
import importlib
import argparse

#Now we go and import all the apps.
app_directory = "apps"
import apps

def load_all_apps():
    subdir_menus = {}
    """ Example of subdir_menus:
    {'apps/network_apps': <ui.menu.Menu instance at 0x7698ac10>, 
    'apps/ee_apps': <ui.menu.Menu instance at 0x7698ab48>, 
    'apps/media_apps': <ui.menu.Menu instance at 0x7698ab70>, 
    'apps/ee_apps/ee_apps': <ui.menu.Menu instance at 0x7695dfa8>, 
    'apps/system_apps': <ui.menu.Menu instance at 0x7698abc0>}
    """
    app_list = {}
    """Example of app_list:
    {'apps/network_apps/wpa_cli': <module 'apps.network_apps.wpa_cli.main' from '/root/WCS/apps/network_apps/wpa_cli/main.py'>, 
    'apps/system_apps/system': <module 'apps.system_apps.system.main' from '/root/WCS/apps/system_apps/system/main.py'>, 
    'apps/skeleton': <module 'apps.skeleton.main' from '/root/WCS/apps/skeleton/main.pyc'>, 
    'apps/media_apps/mocp': <module 'apps.media_apps.mocp.main' from '/root/WCS/apps/media_apps/mocp/main.py'>, 
    'apps/ee_apps/i2ctools': <module 'apps.ee_apps.i2ctools.main' from '/root/WCS/apps/ee_apps/i2ctools/main.py'>, 
    'apps/system_apps/shutdown': <module 'apps.system_apps.shutdown.main' from '/root/WCS/apps/system_apps/shutdown/main.py'>,
    'apps/test': <module 'apps.test.main' from '/root/WCS/apps/test/main.pyc'>, 
    'apps/media_apps/volume': <module 'apps.media_apps.volume.main' from '/root/WCS/apps/media_apps/volume/main.py'>, 
    'apps/network_apps/network': <module 'apps.network_apps.network.main' from '/root/WCS/apps/network_apps/network/main.py'>}
    """
    base_menu = Menu([], i, o, "Main app menu", exitable=False) #Main menu for all applications.
    subdir_menus[app_directory] = base_menu
    for path, subdirs, modules in apps.app_walk(app_directory): 
        """Example of apps.app_walk(directory):  
        [('./apps', ['ee_apps', 'media_apps', 'test', 'system_apps', 'skeleton', 'network_apps'], ['__init__.pyc', '__init__.py']),
        ('./apps/ee_apps', ['i2ctools'], ['__init__.pyc', '__init__.py']),
        ('./apps/ee_apps/i2ctools', [], ['__init__.pyc', '__init__.py', 'main.pyc', 'main.py']),
        ('./apps/media_apps', ['mocp', 'volume'], ['__init__.pyc', '__init__.py']),
        ('./apps/media_apps/mocp', [], ['__init__.pyc', '__init__.py', 'main.pyc', 'main.py']),
        ('./apps/media_apps/volume', [], ['__init__.pyc', '__init__.py', 'main.pyc', 'main.py'])]
        """
        #print("Loading path {} with modules {} and subdirs {}".format(path, modules, subdirs))
        for subdir in subdirs:
            #First, we create subdir menus (not yet linking because they're not created in correct order) and put them in subdir_menus.
            subdir_path = os.path.join(path, subdir)
            subdir_menus[subdir_path] = Menu([], i, o, subdir_path)
        for module in modules:
            #Then, we load modules and store them along with their paths
            try:
                module_path = os.path.join(path, module)
                app = load_app(module_path)
                print("Loaded app {}".format(module_path))
                app_list[module_path] = app
            except Exception as e:
                print("Failed to load app {}".format(module_path))
                print(e)
                Printer(["Failed to load", os.path.split(module_path)[1]], i, o, 2)
    for subdir_path in subdir_menus:
        #Now it's time to link menus to parent menus
        if subdir_path == app_directory:
            continue
        parent_path = os.path.split(subdir_path)[0]
        #print("Adding subdir {} to parent {}".format(subdir_path, parent_path))
        parent_menu = subdir_menus[parent_path]
        subdir_menu = subdir_menus[subdir_path]
        subdir_menu_name = get_subdir_menu_name(subdir_path)
        parent_menu_contents = parent_menu.contents
        parent_menu_contents.append([subdir_menu_name, subdir_menu.activate])
        parent_menu.set_contents(parent_menu_contents)
    for app_path in app_list:
        #Last thing is adding applications to menus.
        app = app_list[app_path]
        subdir_path = os.path.split(app_path)[0]
        #print("Adding app {} to subdir {}".format(app_path, subdir_path))
        subdir_menu = subdir_menus[subdir_path]
        subdir_menu_contents = subdir_menu.contents
        subdir_menu_contents.append([app.menu_name, app.callback])
        subdir_menu.set_contents(subdir_menu_contents)
    #print(app_list)
    #print(subdir_menus)
    return base_menu

def load_app(app_path):
    app_import_path = app_path.replace('/', '.')
    app = importlib.import_module(app_import_path+'.main', package='apps')
    app.init_app(i, o)
    return app

def get_subdir_menu_name(subdir_path):
    """This function gets a subdirectory path and imports __init__.py from it. It then gets _menu_name attribute from __init__.py and returns it. 
    If failed to either import __init__.py or get the _menu_name attribute, it returns the subdirectory name."""
    subdir_import_path = subdir_path.replace('/', '.')
    try:
        subdir_object = importlib.import_module(subdir_import_path+'.__init__')
        return subdir_object._menu_name
    except Exception as e:
        print("Exception while loading __init__.py for subdir {}".format(subdir_path))
        print(e)
        return os.path.split(subdir_path)[1]

def exception_wrapper(callback):
    """This is a wrapper for all applications and menus. It catches exceptions and stops the system the right way when something bad happens, be that a Ctrl+c or an exception in one of the applications."""
    try:
        callback()
    except KeyboardInterrupt:
        Printer(["Does Ctrl+C", "hurt scripts?"], i, o, 0)
        i.atexit()
        sys.exit(1)
    except:
        #raise
        Printer(["A wild exception", "appears!"], i, o, 0)
        i.atexit()
        sys.exit(1)
    else:
        Printer("Exiting pyLCI", i, o, 0)
        i.atexit()
        sys.exit(0)

def launch(name=None):
    """Function that launches pyLCI, either in full mode or single-app mode (if ``name`` kwarg is passed)."""
    if name != None:
        name = name.rstrip('/') #If using autocompletion from main folder, it might append a / at the name end, which isn't acceptable for load_app
        app = load_app(name)
        exception_wrapper(app.callback)
    else:
        app_menu = load_all_apps()
        exception_wrapper(app_menu.activate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pyLCI runner")
    parser.add_argument('-a', '--app', action="store", help="Launch pyLCI with a single app loaded (useful for testing)", default=None)
    args = parser.parse_args()
    launch(name=args.app)
