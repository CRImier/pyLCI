#!/usr/bin/env python

from input import keyboard as kb
#import input
from time import sleep
from menu.menu import Menu
#import menu
from output import screen as scr
#import output
#from phone.modem import ModemInterface
#import phone

#TODO: global setting to replace hardcoded variables
#TODO: start extension mechanism

soundcard_listener = kb.KeyListener(name = 'C-Media Electronics Inc.       USB PnP Sound Device')
numpad_listener = kb.KeyListener(name = 'HID 04d9:1603')
soundcard_listener.listen()
numpad_listener.listen()

#modem = ModemInterface()

def volume_up():
    print "Volume up key pressed"
def volume_down():
    print "Volume down key pressed"

def f1():
    number = "00000000"
    print "Sending an SMS"
    message = "Hi! Imma Wearable Control System"
    #status = modem.send_message(number, message)
"""    if status:
       print "Sending succeeded =)"
    else:
       print "Sending failed =(" """
def f2():
    print "Second function selected"
def f3():
    print "Third function selected"
def f4():
    print "Fourth function selected"
def f5():
    print "Fifth function selected"
def f6():
    print "Sixth function selected"

second_menu_contents = [
["Fourth item", f4],
["Fifth item", f5],
["Sixth item", f6],
["Exit", "exit"]
]

second_menu = Menu(second_menu_contents, scr.send_string, numpad_listener, "Second menu")

main_menu_contents = [
["Send SMS", f1],
["Secondary menu", second_menu.activate],
["Second item", f2],
["Third item", f3]
]

main_menu = Menu(main_menu_contents, scr.send_string, numpad_listener, "Main menu")

print "Main menu:",
print main_menu
print "Second menu:",
print second_menu

main_menu.activate()
