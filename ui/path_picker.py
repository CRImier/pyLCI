import os
import logging
from time import sleep
from threading import Event

from menu import Menu, MenuExitException, to_be_foreground
from printer import Printer

class PathPicker(Menu):
    """#Short description

    """
    no_entry_message = "Empty directory"
    path_chosen = None
    exitable = True
    append_exit = False
    entry_height = 1
    catch_exit = True
    contents_hook = None

    def __init__(self, path, i, o, callback = None, display_hidden = False, current_dot = False, prev_dot = True, scrolling=True):
        """Initialises the Menu object.
        
        Args:

            * ``path``: a path to start from.
            * ``i``, ``o``: input&output device objects.

        Kwargs:

            * ``callback``: if set, FilePickerMenu will call the callback with path as first argument upon selecting path, instead of exiting.
            * ``current_dot``: if set, FilePickerMenu will show '.' path.
            * ``prev_dot``: if set, FilePickerMenu will show '..' path.
            * ``display_hidden``: if set, FilePickerMenu displays hidden files.

        """
        self.i = i
        self.o = o
        if not os.path.isdir(path):
             raise ValueError("PathPicker path has to be a directory!")
        self.path = os.path.normpath(path)
        self.name = "PathPickerMenu-{}".format(self.path)
        self.display_hidden = display_hidden
        self.callback = callback
        self.current_dot = current_dot
        self.prev_dot = prev_dot
        self._in_background = Event()
        self.set_contents([]) #Method inherited from Menu and needs an argument, but context is not right
        self.generate_keymap()
        self.menu_pointers = {}
        self.scrolling={"enabled":scrolling,       
                        "current_finished":False,  
                        "current_scrollable":False,
                        "counter":0,               
                        "pointer":0}               

    def activate(self):
        """ A method which is called when menu needs to start operating. Is blocking, sets up input&output devices, renders the menu and waits until self.in_background is False, while menu callbacks are executed from the input device thread."""
        logging.info("{0} activated".format(self.name))    
        self.o.cursor()
        self.to_foreground() 
        while self.in_background: #All the work is done in input callbacks
            sleep(0.1)
            self.scroll()
        self.o.noCursor()
        logging.debug(self.name+" exited")
        return self.path_chosen

    @to_be_foreground
    def select_element(self):
        """ 
        |Is typically used as a callback from input event processing thread.
        |After callback's execution is finished, sets the keymap again and refreshes the screen.
        |If menu has no elements, exits the menu.
        |If MenuExitException is returned from the callback, exits menu, too."""
        logging.debug("element selected")
        if len(self._contents) > 0:
            self.to_background()
            self._contents[self.pointer][1]()
            self.to_foreground()
            if self.path_chosen:
                self.deactivate()
            else:
                self.to_foreground()

    def generate_keymap(self):
        """Sets the keymap. In the future, will allow per-system keycode-to-callback tweaking using a config file. """
        keymap = {
            "KEY_RIGHT":lambda: self.options_menu(),
            "KEY_UP":lambda: self.move_up(),
            "KEY_DOWN":lambda: self.move_down(),
            "KEY_PAGEUP":lambda: self.page_up(),
            "KEY_PAGEDOWN":lambda: self.page_down(),
            "KEY_KPENTER":lambda: self.select_element(),
            "KEY_ENTER":lambda: self.select_element(),
            "KEY_LEFT": lambda: self.go_back()
            }
        self.keymap = keymap

    def go_back(self):
        if self.path == '/':
            self.deactivate()
            return
        parent_path = os.path.split(self.path)[0]
        self.goto_dir(parent_path)

    def process_contents(self):
        self._contents = []
        self.pointer = 0
        if self.path != '/':
            if self.current_dot or self.prev_dot:
                dot_path = os.path.join(self.path, '.')
                if self.current_dot: self._contents.append(['.', lambda: self.goto_dir(dot_path)])
                if self.prev_dot: self._contents.append(['..', lambda: self.goto_dir(dot_path+'.')])
        path_contents = os.listdir(self.path)
        files = []
        dirs = []
        for item in path_contents:
            full_path = os.path.join(self.path, item)
            if os.path.isdir(full_path):
                if not self.display_hidden or not item.startswith('.'):
                    dirs.append(item)
            else:
                if not self.display_hidden or not item.startswith('.'):
                    files.append(item)
        dirs.sort()
        files.sort()
        for dir in dirs:
            full_path = os.path.join(self.path, dir)
            self._contents.append([dir, lambda x=full_path: self.goto_dir(x)])
        for file in files:
            full_path = os.path.join(self.path, file)
            self._contents.append([file, lambda x=full_path: self.select_path(x)])

    @to_be_foreground
    def options_menu(self):
        self.to_background()
        current_item = self._contents[self.pointer][0]
        full_path = os.path.join(self.path, current_item)
        contents = [["Select path",lambda x=full_path: self.option_select(x)],
                    ["See full name",lambda x=full_path: Printer(current_item, self.i, self.o)],
                    ["See full path",lambda x=full_path: Printer(x, self.i, self.o)],
                    ["Exit PathPicker", self.option_exit]]
        Menu(contents, self.i, self.o).activate()
        self.o.cursor()
        if self.in_background:
            self.to_foreground()

    def option_exit(self):
        self.deactivate()
        raise MenuExitException #Menu needs to exit when PathPicker exits. It doesn't, of course, as it's in the main loop, so the app's left hanging. 
        #One of the reasons MenuExitExceptions are there.

    def option_select(self, path):
        path = os.path.normpath(path)
        if self.callback is None:
            self.select_path(path)
            self.deactivate()
            raise MenuExitException 
        else:
            self.callback(path)
            raise MenuExitException 

    #@to_be_foreground
    def goto_dir(self, dir):
        self.menu_pointers[self.path] = self.pointer
        dir = os.path.normpath(dir)
        self.path = dir
        self.name = "PathPicker-{}".format(self.path)
        self.set_contents([])
        if self.path in self.menu_pointers:
            pointer = self.menu_pointers[self.path]
            #If parent directory changed contents while we were browsing child directory, the count will be different
            #So, a quick check
            if pointer >= len(self._contents):
                self.pointer = len(self._contents)-1
            else:
                self.pointer = pointer
        else:
            self.pointer = 0
        self.refresh()

    #@to_be_foreground
    def select_path(self, path):
        path = os.path.normpath(path)
        if self.callback is not None:
            self.to_background()
            current_item = self._contents[self.pointer][0]
            full_path = os.path.join(self.path, current_item)
            self.callback(full_path)
            self.to_foreground()
        else:
            self.path_chosen = path
