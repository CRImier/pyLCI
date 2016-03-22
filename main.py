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
#import logging
app_menu_contents = [
["App1", lambda: True]
]
try:
    from apps.shutdown import main as shutdown
    shutdown.init_app(i, o)
    app_menu_contents.append([shutdown.menu_name, shutdown.callback])
except:
    o.display_data("Oi", "it crashed")
    raise


app_menu = Menu(app_menu_contents, o, i, "App menu")

def start():
    try:
        app_menu.activate()
    except KeyboardInterrupt:
        input.driver.stop() #Might be needed for some input drivers, such as PiFaceCAD. 
        o.display_data("Does Ctrl+C", "hurt scripts?")
        sys.exit(1)

if __name__ == "__main__":
    start()
