from time import sleep
debug = True

def to_be_foreground(func):
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

def menu_name(func):
    def wrapper(self, *args, **kwargs):
        print self.name+":",
        return func(self, *args, **kwargs)
    return wrapper

class Menu():
    contents = []
    pointer = 0
    display_callback = None
    in_background = True
    in_foreground = False
    exit_flag = False
    name = ""

    @menu_name
    def to_foreground(self):
        if debug: print "menu enabled"
        self.in_background = True
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    @menu_name
    @to_be_foreground
    def to_background(self):
        self.in_foreground = False
        if debug: print "menu disabled"

    @menu_name
    def activate(self):
        if debug: print "menu activated"
        self.to_foreground()
        while self.in_background:
            sleep(1)
        print self.name+" exited"
        return True

    def deactivate(self):
        if debug: print "menu deactivated"    
        self.to_background()
        self.in_background = False

    def print_contents(self):
        print self.contents

    def print_name(self):
        print self.name

    @to_be_foreground
    def move_down(self):
        if debug: print "trying to move up...",
        if self.pointer < (len(self.contents)-1):
            if debug: print "moved down"
            self.pointer += 1  
            self.refresh()    
            return True
        else: 
            print "failed"
            return False

    @to_be_foreground
    def move_up(self):
        if debug: print "trying to move up...",
        if self.pointer != 0:
            if debug: print "moved up"
            self.pointer -= 1
            self.refresh()
            return True
        else: 
            print "failed"
            return False

    @to_be_foreground
    def select_element(self):
        if debug: print "element selected"
        self.to_background()
        self.contents[self.pointer][1]()
        if self.in_background:
            self.to_foreground()

    def generate_keymap(self):
        keymap = {
            "KEY_LEFT":lambda: self.deactivate(),
            "KEY_RIGHT":lambda: self.print_name(),
            "KEY_UP":lambda: self.move_up(),
            "KEY_DOWN":lambda: self.move_down(),
            "KEY_KPENTER":lambda: self.select_element(),
            "KEY_ENTER":lambda: self.select_element()
            }
        self.keymap = keymap

    def __init__(self, contents, callback, listener, name):
        self.generate_keymap()
        self.name = name
        self.listener = listener
        self.contents = contents
        self.process_contents()
        self.set_display_callback(callback)
        

    def process_contents(self):
        for entry in self.contents:
            if entry[1] == "exit":
                entry[1] = self.deactivate
        if debug: print "menu contents processed"

    @menu_name
    @to_be_foreground
    def set_keymap(self):
        self.generate_keymap()
        self.listener.stop_listen()
        self.listener.keymap.clear()
        self.listener.keymap = self.keymap
        print self.keymap
        print self.listener.keymap
        self.listener.listen()

    @menu_name
    @to_be_foreground
    def get_displayed_data(self):
        if self.pointer < (len(self.contents)-1):
            return ("*"+self.contents[self.pointer][0], " "+self.contents[self.pointer+1][0])
        else:
            return (" "+self.contents[self.pointer-1][0], "*"+self.contents[self.pointer][0])

    @menu_name
    @to_be_foreground
    def refresh(self):
        if debug: print "refreshed data on display"
        self.display_callback(*self.get_displayed_data())

    @menu_name
    def set_display_callback(self, callback):
        if debug: print "display callback set"
        self.display_callback = callback

