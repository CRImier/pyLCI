#!/usr/bin/env python

from input import input
from time import sleep
from menu.menu import Menu
from output import output
from subprocess import call


listener = input.listener
screen = output.screen
listener.listen_direct()

#For testing only
#from wlan import wicd_int
#wicd_int.Menu = Menu

def send_sms(name):
    screen.display_data("Sending SMS to:", name)
    sleep(2)
    screen.display_data("Success!", "")
    sleep(2)

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

sms_menu = Menu(sms_menu_contents, screen, listener, "SMS menu")
music_menu = Menu(music_menu_contents, screen, listener, "Music menu")

main_menu_contents = [
["Send SMS", sms_menu.activate],
#["Connect to WiFi", lambda: wicd_int.WicdUserInterface(screen, listener).choose_networks()],
["Music control", music_menu.activate],
["Shutdown", lambda:call(['shutdown', '-h', 'now'])],
]

main_menu = Menu(main_menu_contents, screen, listener, "Main menu")

def start():
    try:
        main_menu.activate()
    except:
        try:
            input.driver.deactivate()
        except:
            pass

if __name__ == "__main__":
    start()
