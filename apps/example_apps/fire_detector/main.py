menu_name = "Flame detector"

from RPi import GPIO
import PIL
import sys
import os

from helpers import ExitHelper
from ui import GraphicsPrinter

app_path = os.path.dirname(sys.modules[__name__].__file__)

def show_image(image_path):
    if not os.path.isabs(image_path):
        image_path = os.path.join(app_path, image_path)
    image = PIL.Image.open(image_path).convert('L')
    GraphicsPrinter(image, i, o, 0.1)

i = None; o = None

def init_app(input, output):
    global i, o
    i = input; o = output

def callback():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN)
    eh = ExitHelper(i).start()
    while eh.do_run():
        state = GPIO.input(18)
        if state:
            show_image("no_fire.png")
        else:
            show_image("fire.png")
