from __future__ import print_function
import wcs
from menu.menu import Menu

from subprocess import call

wm = wcs.wm

application = wm.create_new_application("MOCP control")

window = application.get_window("Main window")

input = window.input_interface
output = window.output_interface

#MOCP commands
def mocp_command(*command):
    return call(['mocp'] + list(command))

def mocp_toggle_play():
    mocp_command("-G")

def mocp_next():
    mocp_command("-f")

def mocp_prev():
    mocp_command("-r")

#amixer commands
def amixer_command(*command):
    return call(['amixer'] + list(command))

def plus_volume():
    return amixer_command("-c", "0", "--", "sset", "PCM", "400+")

def minus_volume():
    return amixer_command("-c", "0", "--", "sset", "PCM", "400-")

def minus_volume():
    return amixer_command("-c", "0", "--", "sset", "PCM", "400-")

def toggle_mute():
    return amixer_command("-c", "0", "--", "sset", "PCM", "toggle")


main_menu_contents = [ 
["Toggle play/pause", mocp_toggle_play],
["Next song", mocp_next],
["Previous song", mocp_prev],
["Increase volume", plus_volume],
["Decrease volume", minus_volume],
["Toggle mute", toggle_mute]
]

menu = Menu(main_menu_contents, output, input, "Main menu", daemon = wcs._daemon)

wcs.register_object(menu)
wcs.start_daemon_thread()

wcs.wm.activate_app(application.number) 

wcs.run(menu.activate, application.shutdown) 
