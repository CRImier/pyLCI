from time import sleep

import logging

def to_be_foreground(func): #A safety check wrapper so that certain checks don't get called if menu is not the one active
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
    first_displayed_entry = 0
    last_displayed_entry = None

    def __init__(self, contents, o, i, name="Menu", entry_height=1):
        self.i = i
        self.o = o
        self.entry_height = entry_height
        self.name = name
        self.generate_keymap()
        self.set_contents(contents)
        self.set_display_callback(o.display_data)

    def to_foreground(self):
        logging.info("menu {0} enabled".format(self.name))    
        self.in_background = True
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    @to_be_foreground
    def to_background(self):
        self.in_foreground = False
        logging.info("menu {0} disabled".format(self.name))    

    def activate(self):
        logging.info("menu {0} activated".format(self.name))    
        self.to_foreground() 
        while self.in_background: #All the work is done in input callbacks
            sleep(1)
        logging.debug(self.name+" exited")
        return True

    def deactivate(self):
        self.in_foreground = False
        self.in_background = False
        logging.info("menu {0} deactivated".format(self.name))    

    def print_contents(self):
        logging.info(self.contents)

    def print_name(self):
        logging.info("Active menu is {0}".format(self.name))    

    @to_be_foreground
    def move_down(self):
        if self.pointer < (len(self.contents)-1):
            logging.debug("moved down")
            self.pointer += 1  
            self.refresh()    
            return True
        else: 
            return False

    @to_be_foreground
    def move_up(self):
        if self.pointer != 0:
            logging.debug("moved up")
            self.pointer -= 1
            self.refresh()
            return True
        else: 
            return False

    @to_be_foreground
    def select_element(self):
        logging.debug("element selected")
        self.to_background()
        if len(self.contents) == 0:
            self.deactivate()
        else:
            if len(self.contents[self.pointer]) > 1:
                self.contents[self.pointer][1]()
        self.set_keymap()        
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

    def set_contents(self, contents):
        self.contents = contents
        self.process_contents()
        #Calculating the highest element displayed
        if len(contents) == 0:
            self.last_displayed_entry = 0
            self.first_displayed_entry = 0
            return True
        full_entries_shown = self.o.rows/self.entry_height
        entry_count = len(self.contents)
        self.first_displayed_entry = 0
        if full_entries_shown > entry_count: #Display is capable of showing more entries than we have, so the last displayed entry is the last menu entry
            print("There are more display rows than entries can take, correcting")
            self.last_displayed_entry = entry_count-1
        else:
            print("There are no empty spaces on the display")
            self.last_displayed_entry = full_entries_shown-1 #We start numbering elements with 0, so 4-row screen would show elements 0-3
        print("First displayed entry is {}".format(self.first_displayed_entry))
        print("Last displayed entry is {}".format(self.last_displayed_entry))
        self.pointer = 0 #Resetting pointer to avoid confusions between changing menu contents

    def process_contents(self):
        for entry in self.contents:
            if len(entry) > 1:
                if entry[1] == "exit":
                    entry[1] = self.deactivate
        logging.debug("{}: menu contents processed".format(self.name))

    @to_be_foreground
    def set_keymap(self):
        self.generate_keymap()
        self.i.stop_listen()
        self.i.keymap.clear()
        self.i.keymap = self.keymap
        self.i.listen_direct()

    def get_displayed_data(self):
        displayed_data = []
        if len(self.contents) == 0:
            return ["No menu entries"]
        if self.pointer < self.first_displayed_entry:
            print("Pointer went too far to top, correcting")
            self.last_displayed_entry -=  self.first_displayed_entry - self.pointer #The difference will mostly be 1 but I reckon it might be more in case of concurrency issues
            self.first_displayed_entry = self.pointer
            print("First displayed entry is {}".format(self.first_displayed_entry))
            print("Last displayed entry is {}".format(self.last_displayed_entry))
        if self.pointer > self.last_displayed_entry:
            print("Pointer went too far to bottom, correcting")
            self.first_displayed_entry += self.pointer - self.last_displayed_entry 
            self.last_displayed_entry = self.pointer
            print("First displayed entry is {}".format(self.first_displayed_entry))
            print("Last displayed entry is {}".format(self.last_displayed_entry))
        disp_entry_positions = range(self.first_displayed_entry, self.last_displayed_entry+1)
        print("Displayed entries: {}".format(disp_entry_positions))
        for entry_num in disp_entry_positions:
            displayed_entry = self.render_displayed_entry(entry_num, active=entry_num == self.pointer)
            displayed_data += displayed_entry
        print("Displayed data: {}".format(displayed_data))
        return displayed_data

    def render_displayed_entry(self, entry_num, active=False):
        rendered_entry = []
        entry_content = self.contents[entry_num][0]
        display_columns = self.o.cols
        if type(entry_content) == str:
            if active:
                rendered_entry.append("*"+entry_content[:display_columns-1]) #First part of string displayed
                entry_content = entry_content[display_columns-1:] #Shifting through the part we just displayed
            else:
                rendered_entry.append(" "+entry_content[:display_columns-1])
                entry_content = entry_content[display_columns-1:]
            for row_num in range(self.entry_height-1): #First part of string done, if there are more rows to display, we give them the remains of string
                rendered_entry.append(entry_content[:display_columns])
                entry_content = entry_content[display_columns:]
        elif type(entry_content) == list:
            entry_content = entry_content[:self.entry_height] #Can't have more arguments in the list argument than maximum entry height
            while len(entry_content) < self.entry_height: #Can't have less either, padding with empty strings if necessary
                entry_content.append('')
            return entry_content
        else:
            raise Exception("Entries may contain either strings or lists of strings as their contents")
        print("Rendered entry: {}".format(rendered_entry))
        return rendered_entry

    @to_be_foreground
    def refresh(self):
        logging.debug("{0}: refreshed data on display".format(self.name))
        self.display_callback(*self.get_displayed_data())

    def set_display_callback(self, callback):
        logging.debug("{0}: display callback set".format(self.name))
        self.display_callback = callback

