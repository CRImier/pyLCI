#!/usr/bin/env python

from input import keyboard as kb
from input import piface2uinput as p2u
#import input
from time import sleep
from menu.menu import Menu
#import menu
from output import screen as scr
#import output
#from phone.modem import ModemInterface
#import phone
from subprocess import call
from wlan import wicd_int
wicd_int.Menu = Menu
wicd_int.scr = scr


#TODO: global setting to replace hardcoded variables
#TODO: start extension mechanism

#soundcard_listener = kb.KeyListener(name = 'C-Media Electronics Inc.       USB PnP Sound Device')
#numpad_listener = kb.KeyListener(name = 'piface-uinput')
piface_listener = p2u.Listener()
piface_listener.start_thread()
numpad_listener = kb.KeyListener(name = 'piface-uinput')

#soundcard_listener.listen()
numpad_listener.listen_direct()
wicd_int.numpad_listener = numpad_listener
#modem = ModemInterface()

def send_sms(name):
    scr.send_string("Sending SMS to:", name)
    sleep(2)
    scr.send_string("Success!", "")
    sleep(2)

"""def connect_to_wifi(name):
    scr.send_string("Connecting to:", name)
    sleep(2)
    if name != 'linksys':
        scr.send_string("Success!", "")
    else:
        scr.send_string("Failure!", "=(")
    sleep(2)

def tether_wifi():
    scr.send_string("Making WiFi AP:", "")
    sleep(2)
    scr.send_string("WiFi AP active!", "")
    sleep(2)
"""

def switch_music():
    pass

music_menu_contents = [
["Next track", switch_music],
["Previous track", switch_music],
["Random track", switch_music],
["Exit", "exit"]
]

sms_menu_contents = [
["SMS to Alice", lambda: send_sms("Alice")],
["SMS to Bob", lambda: send_sms("Bob")],
["SMS to Eve", lambda: send_sms("Eve")],
["Exit", "exit"]
]

"""wifi_menu_contents = [
["linksys", lambda: connect_to_wifi("linksys")],
["RTU-WiFi", lambda: connect_to_wifi("RTU-WiFi")],
["Tethering", lambda: tether_wifi()],
["Exit", "exit"]
]"""

sms_menu = Menu(sms_menu_contents, scr.send_string, numpad_listener, "SMS menu")
#wifi_menu = Menu(wifi_menu_contents, scr.send_string, numpad_listener, "WiFi menu")
music_menu = Menu(music_menu_contents, scr.send_string, numpad_listener, "Music menu")

main_menu_contents = [
["Send SMS", sms_menu.activate],
#["Connect to WiFi", wifi_menu.activate],
["Connect to WiFi", lambda: wicd_int.WicdUserInterface().choose_networks()],
["Music control", music_menu.activate],
["Shutdown", lambda:call("/home/wearable/WCS/halt.sh")],
]

main_menu = Menu(main_menu_contents, scr.send_string, numpad_listener, "Main menu")

def start():
    try:
        main_menu.activate()
    except KeyboardInterrupt:
        piface_listener.listener.deactivate()

if __name__ == "__main__":
    start()
