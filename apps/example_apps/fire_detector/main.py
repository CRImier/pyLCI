menu_name = "Flame detector" #App name as seen in main menu while using the system

from RPi import GPIO
import PIL
import sys
import os

from ui import GraphicsPrinter

app_path = os.path.dirname(sys.modules[__name__].__file__)

def show_image(image_path):
    if not os.path.isabs(image_path):
        image_path = os.path.join(app_path, image_path)
    image = PIL.Image.open(image_path).convert('L')
    GraphicsPrinter(image, i, o, 0.1)

#Some globals for us
i = None #Input device
o = None #Output device

def init_app(input, output):
    global callback, i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN)

def callback():
    while True:
        state = GPIO.input(18)
        if state:
            show_image("no_fire.png")
        else:
            show_image("fire.png")
