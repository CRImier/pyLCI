import os
import logging

from list_ui_base import BaseListBackgroundableUIElement, to_be_foreground
from menu import Menu, MenuExitException
from printer import Printer

class PathPicker(BaseListBackgroundableUIElement):

    path_chosen = None

    def __init__(self, path, i, o, callback = None, display_hidden = False, current_dot = False, prev_dot = True, scrolling=True, **kwargs):
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
        BaseListBackgroundableUIElement.__init__(self, [], i, o, entry_height=1, scrolling=True, append_exit=False)
        if not os.path.isdir(path):
             raise ValueError("PathPicker path has to be a directory!")
        self.display_hidden = display_hidden
        self.callback = callback
        self.current_dot = current_dot
        self.prev_dot = prev_dot
        self.menu_pointers = {}
        self.set_path(os.path.normpath(path))
        self.update_keymap()

    def before_activate(self):
        #Clearing flags
        path_chosen = None

    def get_return_value(self):
        return self.path_chosen

    @to_be_foreground
    def select_entry(self):
        """
        |Is typically used as a callback from input event processing thread.
        |After callback's execution is finished, sets the keymap again and refreshes the screen.
        |If menu has no elements, exits the menu.
        |If MenuExitException is returned from the callback, exits menu, too."""
        logging.debug("element selected")
        if len(self.contents) > 0:
            self.to_background()
            self.contents[self.pointer][1]()
            self.to_foreground()
            if self.path_chosen:
                self.deactivate()
            else:
                self.to_foreground()

    def update_keymap(self):
        """Updates the keymap."""
        self.keymap.update({
            "KEY_RIGHT":lambda: self.options_menu(),
            "KEY_LEFT": lambda: self.go_back()
        })

    def go_back(self):
        if self.path == '/':
            self.deactivate()
            return
        parent_path = os.path.split(self.path)[0]
        self.goto_dir(parent_path)

    def set_path(self, path):
        self.path = path
        self.name = "PathPicker-{}".format(self.path)
        contents = []
        self.pointer = 0
        if self.path != '/':
            if self.current_dot or self.prev_dot:
                dot_path = os.path.join(self.path, '.')
                if self.current_dot: contents.append(['.', lambda: self.goto_dir(dot_path)])
                if self.prev_dot: contents.append(['..', lambda: self.goto_dir(dot_path+'.')])
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
            contents.append([dir, lambda x=full_path: self.goto_dir(x)])
        for file in files:
            full_path = os.path.join(self.path, file)
            contents.append([file, lambda x=full_path: self.select_path(x)])
        self.set_contents(contents)

    @to_be_foreground
    def options_menu(self):
        self.to_background()
        current_item = self.contents[self.pointer][0]
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
        dir = os.path.normpath(dir)
        self.menu_pointers[self.path] = self.pointer
        self.set_path(dir)
        if self.path in self.menu_pointers:
            pointer = self.menu_pointers[self.path]
            #If parent directory changed contents while we were browsing child directory, the count will be different
            #So, a quick check
            if pointer >= len(self.contents):
                self.pointer = len(self.contents)-1
            else:
                self.pointer = pointer
        else:
            self.pointer = 0
        self.view.refresh()

    #@to_be_foreground
    def select_path(self, path):
        path = os.path.normpath(path)
        if self.callback is not None:
            self.to_background()
            current_item = self.contents[self.pointer][0]
            full_path = os.path.join(self.path, current_item)
            self.callback(full_path)
            self.to_foreground()
        else:
            self.path_chosen = path
