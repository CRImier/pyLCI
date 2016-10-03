from time import sleep
from copy import copy
import logging
from threading import Event

def to_be_foreground(func): #A safety check wrapper so that certain checks don't get called if menu is not the one active
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

class MenuExitException(Exception):
    """An exception that you can throw from a menu callback to exit the menu that callback was called from"""
    pass


class Menu():
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
    * ``first_displayed_entry`` : Internal pointer which points to the number of ``self._contents`` element which is at the topmost position of the menu as it's currently displayed on the screen
    * ``last_displayed_entry`` : Internal pointer which points to the number of ``self._contents`` element which is at the lowest position of the menu as it's currently displayed on the screen
    * ``no_entry_message`` : The entry displayed in case menu has no elements

    """
    contents = []
    _contents = []
    pointer = 0
    in_foreground = False
    exit_flag = False
    name = ""
    first_displayed_entry = 0
    last_displayed_entry = None
    exit_exception = False
    no_entry_message = "No menu entries"

    def __init__(self, contents, i, o, name="Menu", entry_height=1, append_exit=True, catch_exit=True, exitable=True):
        """Initialises the Menu object.
        
        Args:

            * ``contents``: a list of values, which can be constructed as described in the Menu object's docstring.
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``name``: Menu name which can be used internally and for debugging.
            * ``entry_height``: number of display rows one menu element occupies.
            * ``append_exit``: Appends an "Exit" alement to menu elements. Doesn't do it if any of elements has callback set as 'exit'.
            * ``catch_exit``: If ``MenuExitException`` is received and catch_exit is False, it passes ``MenuExitException`` to the parent menu so that it exits, too. If catch_exit is True, MenuExitException is not passed along.
            * ``exitable``: Decides if menu can exit at all by pressing ``KEY_LEFT``. Set by default and disables ``KEY_LEFT`` callback if unset. Is used for pyLCI main menu, not advised to be used in other settings.

        """
        self.i = i
        self.o = o
        self.entry_height = entry_height
        self.name = name
        self.append_exit = append_exit
        self.set_contents(contents)
        self.catch_exit = catch_exit
        self.exitable = exitable
        self.generate_keymap()
        self.in_background = Event()


    def to_foreground(self):
        """ Is called when menu's ``activate()`` method is used, sets flags and performs all the actions so that menu can display its contents and receive keypresses. Also, updates the output device with rendered currently displayed menu elements."""
        logging.info("menu {0} enabled".format(self.name))    
        self.in_background.set()
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    @to_be_foreground
    def to_background(self):
        """ Signals ``activate`` to finish executing """
        self.in_foreground = False
        logging.info("menu {0} disabled".format(self.name))    

    def activate(self):
        """ A method which is called when menu needs to start operating. Is blocking, sets up input&output devices, renders the menu and waits until self.in_background is False, while menu callbacks are executed from the input device thread.
        This method also raises MenuExitException if menu exited due to it and ``catch_exit`` is set to False."""
        logging.info("menu {0} activated".format(self.name))    
        self.exit_exception = False
        self.to_foreground() 
        while self.in_background.isSet(): #All the work is done in input callbacks
            sleep(0.1)
        if self.exit_exception:
            if self.catch_exit == False:
                raise MenuExitException
        logging.debug(self.name+" exited")
        return True

    def deactivate(self):
        """ Deactivates the menu completely, exiting it. As for now, pointer state is preserved through menu activations/deactivations """
        self.in_foreground = False
        self.in_background.clear()
        logging.info("menu {0} deactivated".format(self.name))    

    def print_contents(self):
        """ A debug method. Useful for hooking up to an input event so that you can see the representation of menu's contents. """
        logging.info(self._contents)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which menu is currently processing input events. """
        logging.info("Active menu is {0}".format(self.name))    

    @to_be_foreground
    def move_down(self):
        """ Moves the pointer one element down, if possible. 
        |Is typically used as a callback from input event processing thread.
        |TODO: support going from bottom to top when pressing "down" with last menu element selected."""
        if self.pointer < (len(self._contents)-1):
            logging.debug("moved down")
            self.pointer += 1  
            self.refresh()    
            return True
        else: 
            return False

    @to_be_foreground
    def move_up(self):
        """ Moves the pointer one element up, if possible. 
        |Is typically used as a callback from input event processing thread.
        |TODO: support going from top to bottom when pressing "up" with first menu element selected."""
        if self.pointer != 0:
            logging.debug("moved up")
            self.pointer -= 1
            self.refresh()
            return True
        else: 
            return False

    @to_be_foreground
    def select_element(self):
        """ Gets the currently specified element's description from self._contents and executes the callback, if set.
        |Is typically used as a callback from input event processing thread.
        |After callback's execution is finished, sets the keymap again and refreshes the screen.
        |If menu has no elements, exits the menu.
        |If MenuExitException is returned from the callback, exits menu, too."""
        logging.debug("element selected")
        self.to_background()
        if len(self._contents) == 0:
            self.deactivate()
        elif len(self._contents[self.pointer]) > 1:
            try:
                self._contents[self.pointer][1]()
            except MenuExitException:
                self.exit_exception = True
            finally:
                if self.exit_exception:
                    self.deactivate() 
                elif self.in_background.isSet(): #This check is in place so that you can have an 'exit' element
                    self.to_foreground()
        else:
            self.to_foreground()

    def generate_keymap(self):
        """Sets the keymap. In future, will allow per-system keycode-to-callback tweaking using a config file. """
        keymap = {
            "KEY_RIGHT":lambda: self.print_name(),
            "KEY_UP":lambda: self.move_up(),
            "KEY_DOWN":lambda: self.move_down(),
            "KEY_KPENTER":lambda: self.select_element(),
            "KEY_ENTER":lambda: self.select_element()
            }
        if self.exitable:
            keymap["KEY_LEFT"] = lambda: self.deactivate()
        self.keymap = keymap

    def set_contents(self, contents):
        """Sets the menu contents, as well as additionally re-sets ``last`` & ``first_displayed_entry`` pointers and calculates the value for ``last_displayed_entry`` pointer."""
        self.contents = contents
        self.process_contents()
        #Calculating the pointer to last element displayed
        if len(self._contents) == 0:
            self.last_displayed_entry = 0
            self.first_displayed_entry = 0
            return True
        full_entries_shown = self.o.rows/self.entry_height
        entry_count = len(self._contents)
        self.first_displayed_entry = 0
        if full_entries_shown > entry_count: #Display is capable of showing more entries than we have, so the last displayed entry is the last menu entry
            #print("There are more display rows than entries can take, correcting")
            self.last_displayed_entry = entry_count-1
        else:
            #print("There are no empty spaces on the display")
            self.last_displayed_entry = full_entries_shown-1 #We start numbering elements with 0, so 4-row screen would show elements 0-3
        #print("First displayed entry is {}".format(self.first_displayed_entry))
        #print("Last displayed entry is {}".format(self.last_displayed_entry))
        self.pointer = 0 #Resetting pointer to avoid confusions between changing menu contents

    def process_contents(self):
        """Processes contents for custom callbacks. Currently, only 'exit' calbacks are supported.

        If ``self.append_exit`` is set, it goes through the menu and removes every callback which either is ``self.deactivate`` or is just a string 'exit'. 
        |Then, it appends a single ["Exit", 'exit'] element at the end of menu contents. It makes dynamically appending elements to menu easier and makes sure there's only one "Exit" callback, at the bottom of the menu."""
        self._contents = self.contents
        if self.append_exit: 
            element_callbacks = [element[1] if len(element)>1 else None for element in copy(self._contents)]
            for index, callback in enumerate(element_callbacks):
                if callback == 'exit' or callback == self.deactivate:
                    self._contents.pop(index)
            self._contents.append(["Exit", 'exit'])
        for entry in self._contents:
            if len(entry) > 1:
                if entry[1] == "exit":
                    entry[1] = self.deactivate
        logging.debug("{}: menu contents processed".format(self.name))

    @to_be_foreground
    def set_keymap(self):
        """Generate and sets the input device's keycode-to-callback mapping. Re-starts the input device because ofpassing-variables-between-threads issues."""
        self.generate_keymap()
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.listen()

    def get_displayed_data(self):
        """Generates the displayed data in a way that the output device accepts. The output of this function can be fed in the o.display_data function.
        |Corrects last&first_displayed_entry pointers if necessary, then gets the currently displayed elements' numbers, renders each one of them and concatenates them into one big list which it returns.
        |Doesn't support partly-rendering entries yet."""
        displayed_data = []
        if len(self._contents) == 0:
            return [self.no_entry_message]
        if self.pointer < self.first_displayed_entry:
            #print("Pointer went too far to top, correcting")
            self.last_displayed_entry -=  self.first_displayed_entry - self.pointer #The difference will mostly be 1 but I guess it might be more in case of concurrency issues
            self.first_displayed_entry = self.pointer
            #print("First displayed entry is {}".format(self.first_displayed_entry))
            #print("Last displayed entry is {}".format(self.last_displayed_entry))
        if self.pointer > self.last_displayed_entry:
            #print("Pointer went too far to bottom, correcting")
            self.first_displayed_entry += self.pointer - self.last_displayed_entry 
            self.last_displayed_entry = self.pointer
            #print("First displayed entry is {}".format(self.first_displayed_entry))
            #print("Last displayed entry is {}".format(self.last_displayed_entry))
        disp_entry_positions = range(self.first_displayed_entry, self.last_displayed_entry+1)
        #print("Displayed entries: {}".format(disp_entry_positions))
        for entry_num in disp_entry_positions:
            displayed_entry = self.render_displayed_entry(entry_num, active=entry_num == self.pointer)
            displayed_data += displayed_entry
        #print("Displayed data: {}".format(displayed_data))
        return displayed_data

    def render_displayed_entry(self, entry_num, active=False):
        """Renders a menu element by its position number in self._contents, determined also by display width, self.entry_height and element's representation type.
        If element's representation is a string, splits it into parts as long as the display's width in characters.
           If active flag is set, appends a "*" as the first entry's character. Otherwise, appends " ".
           TODO: omit " " and "*" if element height matches the display's row count.
        If element's representation is a list, it returns that list as the rendered entry, trimming its elements down or padding the list with empty strings to match the element's height as defined.
        """
        rendered_entry = []
        entry_content = self._contents[entry_num][0]
        display_columns = self.o.cols
        if type(entry_content) in [str, unicode]:
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
            return [str(element) for element in entry_content]
        else:
            raise Exception("Entries may contain either strings or lists of strings as their representations")
        #print("Rendered entry: {}".format(rendered_entry))
        return rendered_entry

    @to_be_foreground
    def refresh(self):
        logging.debug("{0}: refreshed data on display".format(self.name))
        self.o.display_data(*self.get_displayed_data())
