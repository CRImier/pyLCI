from __future__ import print_function
from menu.menu import Menu

import time
import threading

import Pyro4
import Pyro4.util

#Pyro4.config.REQUIRE_EXPOSE = True

wm = Pyro4.Proxy("PYRONAME:wcs.window_manager")

#name = raw_input("Input application name:")
application = wm.get_application("Application 1")

#name = raw_input("Input window name:")
window = application.get_window("Window 1")

input = window.input_interface
output = window.output_interface

main_menu_contents = [ 
["Send SMS", lambda: print("Sending SMS")],
["Connect to WiFi", lambda: print("Choosing WiFi")],
["Music control", lambda: print("Controlling music")],
["Shutdown", lambda: print("Shutting down")]
]

daemon = Pyro4.Daemon()

menu = Menu(main_menu_contents, output, input, "Main menu", daemon = daemon)

daemon.register(menu)

wm.activate_current_window()

thread = threading.Thread(target=daemon.requestLoop)
thread.daemon = True
thread.start()

time.sleep(2)

print(dir(menu))
print(dir(menu.listener))
print(dir(menu.screen))

try:
    menu.activate()
except Exception:
    print("Pyro traceback:")
    print("".join(Pyro4.util.getPyroTraceback()))

application.destroy_window(window)
