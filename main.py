#!/usr/bin/env python

from input import input
from menu.menu import Menu
from output import output
from wm import window_manager, wm_menu

from time import sleep
from subprocess import call

def start_io():
    print("Starting IO drivers.")
    global listener
    global screen
    listener = input.listener
    screen = output.screen
    listener.listen_direct()

def run_wm(app_object):
    wmr = window_manager.WindowManagerRunner(listener, screen)
    wmr.run(app_object)

if __name__ == "__main__":
    try:
        start_io()
        run_wm(wm_menu.WindowManagerMenu)
    except:
        #input.driver.deactivate()
        raise


