import os
import logging
from time import sleep

from menu import Menu, to_be_foreground
from printer import Printer

class PathPicker():
    def __init__ (self, initial_path, i, o, name="PathPicker"):
        if not os.path.isdir(initial_path):
             raise ValueError("PathPicker path has to be a directory!")
        self.path = initial_path
        self.i = i
        self.o = o
        self.name = name
    
    def activate(self):
        """ A method that activates PathPicker. Returns path chosen in the end - or None if there wasn't."""
        path = PathPickerMenu(self.path, self.i, self.o).activate()
        return path

class PathPickerMenu(Menu):
    """Implements a menu which can be used to navigate through your application, output a list of values or select actions to perform. Is one of the most used elements, used both in system core and in most of the applications.

    Attributes:

    * ``contents``: list of menu elements which was passed either to ``Menu`` constructor or to ``menu.set_contents()``.
       
      Menu element structure is a list, where:
         * ``element[0]`` (element's representation) is either a string, which simply has the element's value as it'll be displayed, such as "Menu element 1", or, in case of entry_height > 1, can be a list of strings, each of which represents a corresponding display row occupied by the element.
         * ``element[1]`` (element's callback) is a function which is called when menu's element is activated (such as pressing ENTER button when menu's element is selected). 
           * Can be omitted if you don't need to have any actions taken upon activation of the element.
           * Can be specified as 'exit' if you want a menu element that exits the menu upon activation.

      *If you want to set contents after the initalisation, please, use set_contents() method.*
    * ``_contents``: "Working copy" of menu contents, basically, a ``contents`` attribute which has been processed by ``self.process_contents``. 
    * ``pointer``: currently selected menu element's number in ``self._contents``.
    * ``in_background``: a flag which indicates if menu is currently active, either if being displayed or being in background (for example, if a sub-menu of this menu is currently active)
    * ``in_foreground`` : a flag which indicates if menu is currently displayed. If it's not active, inhibits any of menu's actions which can interfere with other menu or UI element being displayed.
    * ``first_displayed_entry`` : Internal flag which points to the number of ``self._contents`` element which is at the topmost position of the menu as it's currently displayed on the screen
    * ``last_displayed_entry`` : Internal flag which points to the number of ``self._contents`` element which is at the lowest position of the menu as it's currently displayed on the screen

    """
    no_entry_message = "Empty directory"
    path_chosen = False
    exitable = True
    append_exit = False
    entry_height = 1
    catch_exit = True
    exit_flag = False

    def __init__(self, path, i, o, display_hidden = False):
        """Initialises the Menu object.
        
        Args:

            * ``path``: a path to list the contents of.
            * ``i``, ``o``: input&output device objects.

        Kwargs:

            * ``display_hidden``: if set, FilePickerMenu displays hidden files.

        """
        self.i = i
        self.o = o
        self.path = path
        self.name = "PathPickerMenu-{}".format(self.path)
        self.display_hidden = display_hidden
        self.set_contents(self.path) #As a side effect, self.contents is set to self.path (self._contents is properly set)
        self.set_display_callback(o.display_data)
        self.generate_keymap()

    def activate(self):
        """ A method which is called when menu needs to start operating. Is blocking, sets up input&output devices, renders the menu and waits until self.in_background is False, while menu callbacks are executed from the input device thread."""
        logging.info("{0} activated".format(self.name))    
        self.to_foreground() 
        while self.in_background and not self.exit_flag: #All the work is done in input callbacks
            sleep(0.1)
        self.deactivate()
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
        if len(self._contents) == 0:
            self.exit_flag = True
        else:
            self.to_background()
            path = self._contents[self.pointer][1]()
            if path:
                self.path_chosen = path
                self.deactivate()
            elif self.path_chosen:
                exit_flag = True
            else:
                 self.to_foreground()

    def generate_keymap(self):
        """Sets the keymap. In the future, will allow per-system keycode-to-callback tweaking using a config file. """
        keymap = {
            "KEY_RIGHT":lambda: self.options_menu(),
            "KEY_UP":lambda: self.move_up(),
            "KEY_DOWN":lambda: self.move_down(),
            "KEY_KPENTER":lambda: self.select_element(),
            "KEY_ENTER":lambda: self.select_element(),
            "KEY_LEFT": lambda: self.deactivate()
            }
        self.keymap = keymap

    def process_contents(self, path):
        """ """
        self._contents = []
        path_contents = os.listdir(self.path)
        files = []
        dirs = []
        for item in path_contents:
            full_path = os.path.join(self.path, item)
            if os.path.isdir(full_path):
                if not self.display_hidden or not item.startswith('.'):
                    dirs.append(item)
            elif os.path.isfile(full_path):
                if not self.display_hidden or not item.startswith('.'):
                    files.append(item)
            else:
                print("PathPicker: WUUUUUUUT is dis: {}".format(full_path))
        dirs.sort()
        files.sort()
        for dir in dirs:
            full_path = os.path.join(self.path, dir)
            self._contents.append([dir, lambda x=full_path: self.path_menu(x)])
        for file in files:
            full_path = os.path.join(self.path, file)
            self._contents.append([file, lambda x=full_path: self.select_path(x)])
        logging.debug("{}: contents processed".format(self.name))

    @to_be_foreground
    def options_menu(self):
        current_item = self._contents[self.pointer][0]
        full_path = os.path.join(self.path, current_item)
        contents = [["Select path",lambda x=full_path: self.select_path(x)],
                    ["See full name",lambda x=full_path: Printer(current_item, self.i, self.o)]]
        Menu(contents, self.i, self.o).activate()
        self.set_keymap()
        self.refresh()

    #@to_be_foreground
    def path_menu(self, path):
        return PathPickerMenu(path, self.i, self.o).activate()

    #@to_be_foreground
    def select_path(self, path):
        self.set_keymap()
        self.path_chosen = path
        self.exit_flag = True

    @to_be_foreground
    def set_keymap(self):
        """Generate and sets the input device's keycode-to-callback mapping. Re-starts the input device because ofpassing-variables-between-threads issues."""
        self.generate_keymap()
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.listen()
