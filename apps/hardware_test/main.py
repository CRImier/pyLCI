menu_name = "Hardware test"

from threading import Event, Thread
from traceback import format_exc
from subprocess import call
from time import sleep
import sys
import os

from ui import Menu, Printer, PrettyPrinter

i = None
o = None

#Code from downloading a song from http://freemusicarchive.org/
downloaded = Event()
music_filename = "test.mp3"
url = "https://freemusicarchive.org/music/download/cb244f71bd004b784fbd31a357c4f717c358cfc9"
base_dir = os.path.dirname(sys.modules[__name__].__file__)
music_path = os.path.join(base_dir, music_filename)

def init_app(input, output):
    global i, o
    i = input; o = output
    if music_filename not in os.listdir(base_dir):
        def download():
            downloaded.clear()
            print("Downloading music for hardware test app!")
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
        try:
            bus.read_byte(0x20)
        except IOError as e:
            if e.errno == 16:
                PrettyPrinter("IO expander not found!", i, o)
            elif e.errno == 121:
                PrettyPrinter("IO expander OK!", i, o)
        else:
            PrettyPrinter("IO expander driver not loaded!", i, o)
        #Launching splashscreen
        import splash
        splash.splash(i, o)
        sleep(2)
        #Launching key_test app from app folder, that's symlinked from example app folder
        PrettyPrinter("Testing keypad", i, o, 1)
        import key_test
        key_test.init_app(i, o)
        key_test.callback()
        #Testing the RGB LED
        PrettyPrinter("Testing RGB LED", i, o, 1)
        import zerophone
        led = zerophone.RGB_LED()
        for color in ["red", "green", "blue"]:
            led.set_color(color)
            Printer(color.center(o.cols), i, o, 3)
        led.set_color("none")
        #Testing audio jack sound
        PrettyPrinter("Testing audio jack", i, o, 1)
        if not downloaded.isSet():
            PrettyPrinter("Audio jack test music not yet downloaded, waiting...", i, o)
            downloaded.wait()
        PrettyPrinter("Press C1 to restart music, C2 to continue testing", i, o)
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play()
        continue_event = Event()
        def restart():
            print("Restarting")
            pygame.mixer.music.stop()
            pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
        def stop():
            print("Stopping")
            pygame.mixer.music.stop()
            continue_event.set()
        i.clear_keymap()
        i.set_callback("KEY_F1", restart)
        i.set_callback("KEY_F2", stop)
        continue_event.wait()
        #Self-test passed, it seems!
                
    except:
        exc = format_exc()
        PrettyPrinter(exc, i, o, 10)
    else:
        PrettyPrinter("Self-test passed!", i, o, 3)
