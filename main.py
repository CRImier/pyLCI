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
    #input.init()
    i = None
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
import apps

def launch(name=None):
    if name != None:
        app = load_app(name)
        exception_wrapper(app.callback)
    else:
        app_menu_contents = load_all_apps()
        print(app_menu_contents)
        #app_menu = Menu(app_menu_contents, i, o, "App menu", append_exit=False)
        #exception_wrapper(app_menu.activate)

def exception_wrapper(callback):
    try:
        callback()
    except KeyboardInterrupt:
        Printer(["Does Ctrl+C", "hurt scripts?"], i, o, 0)
        i.atexit()
        sys.exit(1)
    except:
        Printer(["A wild exception", "appears!"], i, o, 0)
        i.atexit()
        raise
    else:
        Printer("Exiting pyLCI", i, o, 0)
        i.atexit()
        sys.exit(0)


def load_all_apps():
    menu_contents = []
    app_walk = apps.app_walk('apps')
    app_list = {}
    for path, subdirs, modules in app_walk:
        print("Loading path {} with modules {} and subdirs {}".format(path, modules, subdirs))
        current_menu = None
        current_menu_contents = []
        for module in modules:
            try:
                module_path = os.path.join(path, module)
                module_import_path = module_path.replace('/', '.')
                print(module_import_path)
                app = load_app(module_import_path)
                app_list[module_path] = app
                #menu_contents.append([app.menu_name, app.callback])
            except Exception as e:
                print("Failed to load {}".format(module_path))
                print(e)
                #Printer(["Failed to load", app_name], i, o, 2)
                raise
            
        for subdir in subdirs:
            pass        
    return app_list

def load_app(app_import_path):
    #global app_list
    app = importlib.import_module(app_import_path+'.main', package='apps')
    app.init_app(i, o)
    #app_list[app_name] = app_import
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pyLCI runner")
    parser.add_argument('-a', '--app', action="store", help="Launch pyLCI with a single app loaded (useful for testing)", default=None)
    args = parser.parse_args()
    launch(name=args.app)
