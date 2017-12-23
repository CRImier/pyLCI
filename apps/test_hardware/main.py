import logging

from helpers.logger import setup_logger

menu_name = "Hardware test"

from threading import Event, Thread
from traceback import format_exc
from subprocess import call
from time import sleep
import sys
import os

from ui import Menu, Printer, PrettyPrinter, GraphicsPrinter
from helpers import ExitHelper, local_path_gen

logger = setup_logger(__name__, logging.WARNING)

i = None
o = None

#Code from downloading a song from http://freemusicarchive.org/
downloaded = Event()
url = "http://wiki.zerophone.org/images/b/b5/Otis_McMusic.mp3"

music_filename = "test.mp3"
local_path = local_path_gen(__name__)
music_path = local_path(music_filename)

def init_app(input, output):
    global i, o
    i = input; o = output
    if music_filename not in os.listdir(local_path('.')):
        def download():
            downloaded.clear()
            logger.debug("Downloading music for hardware test app!")
            call(["wget", url, "-O", music_path])
            downloaded.set()
        t = Thread(target=download)
        t.daemon=True
        t.start()
    else:
        downloaded.set()

def callback():
    try:
        #Testing I2C - 0x12 should answer, 0x20 should raise IOError with busy errno
        from smbus import SMBus
        bus = SMBus(1)
        try:
            bus.read_byte(0x12)
        except IOError:
            PrettyPrinter("Keypad does not respond!", i, o)
        else:
            PrettyPrinter("Keypad found!", i, o)
        #Checking IO expander
        expander_ok = False
        try:
            bus.read_byte(0x20)
        except IOError as e:
            if e.errno == 16:
                PrettyPrinter("IO expander OK!", i, o)
                expander_ok = True
            elif e.errno == 121:
                PrettyPrinter("IO expander not found!", i, o)
        else:
            PrettyPrinter("IO expander driver not loaded!", i, o)
        #Launching splashscreen
        GraphicsPrinter("splash.png", i, o, 2)
        #Launching key_test app from app folder, that's symlinked from example app folder
        PrettyPrinter("Testing keypad", i, o, 1)
        import key_test
        key_test.init_app(i, o)
        key_test.callback()
        #Following things depend on I2C IO expander,
        #which might not be present:
        if expander_ok:
            #Testing charging detection
            PrettyPrinter("Testing charger detection", i, o, 1)
            from zerophone_hw import is_charging
            eh = ExitHelper(i, ["KEY_LEFT", "KEY_ENTER"]).start()
            if is_charging():
                PrettyPrinter("Charging, unplug charger to continue \n Enter to bypass", None, o, 0)
                while is_charging() and eh.do_run():
                    sleep(1)
            else:
                PrettyPrinter("Not charging, plug charger to continue \n Enter to bypass", None, o, 0)
                while not is_charging() and eh.do_run():
                    sleep(1)
            #Testing the RGB LED
            PrettyPrinter("Testing RGB LED", i, o, 1)
            from zerophone_hw import RGB_LED
            led = RGB_LED()
            for color in ["red", "green", "blue"]:
                led.set_color(color)
                Printer(color.center(o.cols), i, o, 3)
            led.set_color("none")
        #Testing audio jack sound
        PrettyPrinter("Testing audio jack", i, o, 1)
        if not downloaded.isSet():
            PrettyPrinter("Audio jack test music not yet downloaded, waiting...", i, o)
            downloaded.wait()
        disclaimer = ["Track used:" "", "Otis McDonald", "-", "Otis McMusic", "YT AudioLibrary"]
        Printer([s.center(o.cols) for s in disclaimer], i, o, 3)
        PrettyPrinter("Press C1 to restart music, C2 to continue testing", i, o)
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play()
        continue_event = Event()
        def restart():
            pygame.mixer.music.stop()
            pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
        def stop():
            pygame.mixer.music.stop()
            continue_event.set()
        i.clear_keymap()
        i.set_callback("KEY_F1", restart)
        i.set_callback("KEY_F2", stop)
        i.set_callback("KEY_ENTER", stop)
        continue_event.wait()
        #Self-test passed, it seems!
    except:
        exc = format_exc()
        PrettyPrinter(exc, i, o, 10)
    else:
        PrettyPrinter("Self-test passed!", i, o, 3, skippable=False)
