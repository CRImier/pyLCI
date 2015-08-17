from __future__ import print_function
import wcs
from menu.menu import Menu

wm = wcs.wm

application = wm.create_new_application("Application 1")

window = application.get_window("Window 1")

input = window.input_interface
output = window.output_interface

main_menu_contents = [ 
["Send SMS", lambda: print("Sending SMS")],
["Connect to WiFi", lambda: print("Choosing WiFi")],
["Music control", lambda: print("Controlling music")],
["Shutdown", lambda: print("Shutting down")]
]

menu = Menu(main_menu_contents, output, input, "Main menu", daemon = wcs._daemon)

wcs.register_object(menu)
wcs.start_daemon_thread()

wm.activate_app(0)

wcs.run(menu.activate, application.shutdown) 
