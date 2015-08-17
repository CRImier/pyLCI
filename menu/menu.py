from time import sleep
from threading import Thread
import logging
import Pyro4

def to_be_foreground(func):
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

class Menu():
    contents = []
    pointer = 0
    display_callback = None
    in_background = True
    in_foreground = False
    exit_flag = False
    name = ""
    _keymap = None

    def __init__(self, contents, screen, listener, name, daemon = None):
        self.generate_keymap()
        self.name = name
        self.listener = listener
        self._daemon = daemon
        self.contents = contents
        self.process_contents()
        self.screen = screen
        self.display_callback = screen.display_data
        self.set_display_callback(self.display_callback)

    def to_foreground(self):
        logging.info("menu {0} enabled".format(self.name))    
        self.in_background = True
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    @to_be_foreground
    def to_background(self):
        self.listener.clear_keymap()
        self.in_foreground = False
        logging.info("menu {0} disabled".format(self.name))    

    @Pyro4.callback
    def activate(self):
        logging.info("menu {0} activated".format(self.name))    
        self.to_foreground()
        while self.in_background:
            sleep(1)
        logging.debug(self.name+" exited")
        return True

    @Pyro4.callback
    def deactivate(self):
        logging.info("menu {0} deactivated".format(self.name))    
        self.to_background()
        self.in_background = False

    @Pyro4.callback
    def print_contents(self):
        logging.info(self.contents)

    @Pyro4.callback
    def print_name(self):
        logging.info("Active menu is {0}".format(self.name))    

    @Pyro4.callback
    @to_be_foreground
    def move_down(self):
        if self.pointer < (len(self.contents)-1):
            logging.debug("moved down")
            self.pointer += 1  
            self.refresh()    
            return True
        else: 
            return False

    @Pyro4.callback
    @to_be_foreground
    def move_up(self):
        if self.pointer != 0:
            logging.debug("moved up")
            self.pointer -= 1
            self.refresh()
            return True
        else: 
            return False

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

    def generate_keymap(self):
        keymap = {
            "KEY_LEFT":["deactivate", self],
            "KEY_RIGHT":["print_name", self],
            "KEY_UP":["move_up",self],
            "KEY_DOWN":["move_down",self],
            "KEY_KPENTER":["select_element",self],
            "KEY_ENTER":["select_element",self]
        }
        self._keymap = keymap

    @Pyro4.callback
    def process_contents(self):
        for entry in self.contents:
            if entry[1] == "exit":
                entry[1] = self.deactivate
        logging.debug("{0}: menu contents processed".format(self.name))

    @to_be_foreground
    def set_keymap(self):
        self.generate_keymap()
        self.listener.stop_listen()
        self.listener.clear_keymap()
        self.listener.set_keymap(self._keymap)
        self.listener.listen()

    @to_be_foreground
    def get_displayed_data(self):
        if len(self.contents) == 0:
            return ("No menu entries", " ")
        elif len(self.contents) == 1:
            return ("*"+self.contents[0][0], " ")
        elif self.pointer < (len(self.contents)-1):
            return ("*"+self.contents[self.pointer][0], " "+self.contents[self.pointer+1][0])
        else:
            return (" "+self.contents[self.pointer-1][0], "*"+self.contents[self.pointer][0])

    @Pyro4.callback
    @to_be_foreground
    def refresh(self):
        logging.debug("{0}: refreshed data on display".format(self.name))
        self.display_callback(*self.get_displayed_data())

    def set_display_callback(self, callback):
        logging.debug("{0}: display callback set".format(self.name))
        self.display_callback = callback

