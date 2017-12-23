import logging

from helpers.logger import setup_logger

menu_name = "Number input app"

from datetime import datetime

from ui import IntegerInDecrementInput as Input

logger = setup_logger(__name__, logging.INFO)

i = None #Input device
o = None #Output device

#Callback for ZPUI. It gets called when application is activated in the main menu
def callback():
    number_input = Input(0, i, o)
    logger.info(number_input.activate())

def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals

