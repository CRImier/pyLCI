from time import sleep
from threading import Thread
import logging
import Pyro4

from ui import ListView #Base class we'll be instantiating

def to_be_foreground(func):
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

class Menu(ListView):

    in_background = True
    exit_flag = False

    #TODO: make this configurable
    keymap_base = {
        "KEY_LEFT":"deactivate",
        "KEY_RIGHT":"print_name",
        "KEY_UP":"move_up",
        "KEY_DOWN":"move_down",
        "KEY_KPENTER":"select_element",
        "KEY_ENTER":"select_element"
    }

    def __init__(self, *args):
        ListView.__init__(self, *args)

    def to_foreground(self):
        self.in_background = True
        ListView.to_foreground(self)

    @to_be_foreground
    def to_background(self):
        self.listener.clear_keymap()
        self.in_foreground = False
        logging.info("{0} {1} disabled".format(self.type, self.name))    

    @Pyro4.callback
    def activate(self):
        logging.info("{0} {1} activated".format(self.type, self.name))    
        self.to_foreground()
        while self.in_background:
            sleep(1)
        logging.debug(self.name+" exited")
        return True

    @Pyro4.callback
    def deactivate(self):
        logging.info("{0} {1} deactivated".format(self.type, self.name))
        self.to_background()
        self.in_background = False

    @Pyro4.callback
    @to_be_foreground
    def select_element(self):
        logging.debug("element selected")
        self.to_background()
        if len(self.contents) == 0:
            pass
        else:
            self.contents[self.pointer][1]()
        if self.in_background:
            self.to_foreground()
            self.set_keymap()        

    @Pyro4.callback
    def process_contents(self):
        for entry in self.contents:
            if entry[1] == "exit":
                entry[1] = self.deactivate
        logging.debug("{0}: menu contents processed".format(self.name))
