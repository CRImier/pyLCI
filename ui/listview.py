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

class ListView():
    contents = []
    pointer = 0
    display_callback = None
    in_foreground = True
    name = ""
    _keymap = None

    type = "listbox"

    keymap_base = {
        "KEY_LEFT":"deactivate",
        "KEY_RIGHT":"print_name",
        "KEY_UP":"move_up",
        "KEY_DOWN":"move_down"
    }

    empty_placeholder = "No entries"

    def __init__(self, contents, input, output, name, daemon = None):
        self.generate_keymap()
        self.name = name
        self.listener = listener
        self._daemon = daemon
        self.contents = contents
        self.process_contents()
        self.screen = screen
        self.display_callback = output.display_data
        self.set_display_callback(self.display_callback)

    def to_foreground(self):
        logging.info("{0} {1} enabled".format(self.type, self.name))    
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    @Pyro4.callback
    def activate(self):
        logging.info("{0} {1} activated".format(self.type, self.name))    
        self.to_foreground()
        while self.in_foreground:
            sleep(1)
        logging.debug(self.name+" exited")
        return True

    @Pyro4.callback
    @to_be_foreground
    def deactivate(self):
        logging.info("{0} {1} deactivated".format(self.type, self.name))    
        self.in_foreground = False

    @Pyro4.callback
    @to_be_foreground
    def print_contents(self):
        logging.info(self.contents)

    @Pyro4.callback
    @to_be_foreground
    def print_name(self):
        logging.info("{0} {1} is currently active".format(self.type, self.name))    

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

    def generate_keymap(self):
        keymap = {}
        for key in self.keymap_base.keys():    
            key_func_name = keymap_base[key]   
            keymap[key] = [key_func_name, self]
        self._keymap = keymap

    @to_be_foreground
    def set_keymap(self): #TODO: change to apply_keymap()
        self.generate_keymap()
        self.listener.stop_listen()
        self.listener.clear_keymap()
        self.listener.set_keymap(self._keymap)
        self.listener.listen()

    @to_be_foreground
    def get_displayed_data(self):
        if len(self.contents) == 0:
            return (self.empty_placeholder, " ")
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

