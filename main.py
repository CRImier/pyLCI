#!/usr/bin/env python
import sys
#Welcome to pyLCS innards
#Here, things are about i and o, which are input and output
#And we output things for debugging, so o goes first.
from output import output

#These lines are here so that welcome screen stays on a little longer:
o = output.screen
o.display_data("Welcome to", "pyLCS")

try:
    #All the LCS-related modules are imported here
    from input import input
    from menu.menu import Menu
    #Now we init the input.
    input.init(o)
    i = input.listener
    i.listen_direct()
    #from apps import app_list
except:
    o.display_data("Oops. :(", "y u make mistake") #Yeah, that's about all the debug data. 
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
app_list = {}

def launch(name=None):
    if name != None:
        app = load_app(name)
        ctrl_c_wrapper(app.callback)
    else:
        app_menu_contents = load_all_apps()
        app_menu = Menu(app_menu_contents, o, i, "App menu")
        ctrl_c_wrapper(app_menu.activate)

def ctrl_c_wrapper(callback):
    try:
        callback()
    except KeyboardInterrupt:
        input.driver.stop() #Might be needed for some input drivers, such as PiFaceCAD. 
        o.display_data("Does Ctrl+C", "hurt scripts?")
        sys.exit(1)

def load_all_apps():
    menu_contents = []
    app_names = apps.module_names
    for app_name in app_names:
        print(app_name)
        try:
            app = load_app(app_name)
            menu_contents.append([app.menu_name, app.callback])
        except Exception as e:
            o.display_data("Failed to import", app_name)
            print(e)
            sleep(3)
            #raise
    return menu_contents

def load_app(name):
    global app_list
    app = importlib.import_module('apps.'+name+'.main')
    app.init_app(i, o)
    app_list[name] = app
    return app    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pyLCS runner")
    parser.add_argument('-a', '--app', action="store", help="Launch pyLCS with a single app loaded (useful for testing)", default=None)
    args = parser.parse_args()
    launch(name=args.app)
