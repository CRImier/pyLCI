from time import sleep
from copy import copy
import logging

def to_be_foreground(func): #A safety check wrapper so that certain checks don't get called if menu is not the one active
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

class Checkbox():
    """Implements a checkbox which can be used to enable or disable some functions in your application. 

    Attributes:

    * ``contents``: list of checkbox elements which was passed either to ``Checkbox`` constructor or to ``checkbox.set_contents()``.
       
      Checkbox element structure is a list, where:
         * ``element[0]`` (element's representation) is either a string, which simply has the element's value as it'll be displayed, such as "Menu element 1", or, in case of entry_height > 1, can be a list of strings, each of which represents a corresponding display row occupied by the element.
         * ``element[1]`` (element's name) is a name returned by the checkbox upon its exit in a dictionary along with its boolean value.
         * ``element[2]`` (element's state) is the default state assumed by the checkbox. If not present, assumed to be default_state.

      *If you want to set contents after the initalisation, please, use set_contents() method.*
    * ``_contents``: "Working copy" of checkbox contents, basically, a ``contents`` attribute which has been processed by ``self.process_contents``. 
    * ``pointer``: currently selected menu element's number in ``self._contents``.
    * ``in_foreground`` : a flag which indicates if checkbox is currently displayed. If it's not active, inhibits any of menu's actions which can interfere with other menu or UI element being displayed.
    * ``first_displayed_entry`` : Internal flag which points to the number of ``self._contents`` element which is at the topmost position of the checkbox menu as it's currently displayed on the screen
    * ``last_displayed_entry`` : Internal flag which points to the number of ``self._contents`` element which is at the lowest position of the checkbox menu as it's currently displayed on the screen

    """
    contents = []
    _contents = []
    pointer = 0
    in_foreground = False
    name = ""
    first_displayed_entry = 0
    last_displayed_entry = None
    states = []

    def __init__(self, contents, i, o, name="Menu", entry_height=1, default_state=False, final_button_name="Save"):
        """Initialises the Checkbox object.
        
        Args:

            * ``contents``: a list of element descriptions, which can be constructed as described in the Checkbox object's docstring.
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``name``: Checkbox name which can be used internally and for debugging.
            * ``entry_height``: number of display rows one checkbox element occupies.
            * ``default_state``: default state of the element if not supplied.

        """
        self.i = i
        self.o = o
        self.entry_height = entry_height
        self.final_button_name = final_button_name
        self.name = name
        self.set_contents(contents)
        self.generate_keymap()

    def to_foreground(self):
        """ Is called when checkboxes ``activate()`` method is used, sets flags and performs all the actions so that checkbox can display its contents and receive keypresses. Also, updates the output device with rendered currently displayed checkbox elements."""
        logging.info("checkbox {0} enabled".format(self.name))    
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        """ A method which is called when checkbox needs to start operating. Is blocking, sets up input&output devices, renders the checkbox and waits until self.in_background is False, while checkbox callbacks are executed from the input device thread."""
        logging.info("checkbox {0} activated".format(self.name))    
        self.o.cursor()
        self.to_foreground()
        while self.in_foreground: #All the work is done in input callbacks
            sleep(0.1)
        self.o.noCursor()
        logging.debug(self.name+" exited")
        return {self._contents[index][1]:self.states[index] for index, element in enumerate(self._contents)}

    @to_be_foreground
    def deactivate(self):
        """ Deactivates the menu completely, exiting it. As for now, pointer state is preserved through checkbox activations/deactivations """
        self.in_foreground = False
        logging.info("checkbox {0} deactivated".format(self.name))    

    def print_contents(self):
        """ A debug method. Useful for hooking up to an input event so that you can see the representation of checkbox's contents. """
        logging.info(self._contents)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which UI element is currently processing input events. """
        logging.info("Active menu is {0}".format(self.name))    

    @to_be_foreground
    def move_down(self):
        """ Moves the pointer one element down, if possible. 
        |Is typically used as a callback from input event processing thread.
        |TODO: support going from bottom to top when pressing "down" with last checkbox element selected."""
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
        |TODO: support going from top to bottom when pressing "up" with first checkbox element selected."""
        if self.pointer != 0:
            logging.debug("moved up")
            self.pointer -= 1
            self.refresh()
            return True
        else: 
            return False

    @to_be_foreground
    def flip_state(self):
        """ Changes the current element's state to the opposite.
        |Is typically used as a callback from input event processing thread. Afterwards, refreshes the screen."""
        logging.debug("element selected")
        if len(self._contents) == 0:
            self.deactivate()
        else:
            if self._contents[self.pointer][2] == 'exit':
                self.deactivate()
                return
            self.states[self.pointer] = not self.states[self.pointer] #Just inverting.
            self.refresh()
                
    def generate_keymap(self):
        """Sets the keymap. In future, will allow per-system keycode-to-callback tweaking using a config file. """
        keymap = {
            "KEY_RIGHT":lambda: self.print_name(),
            "KEY_LEFT":lambda: self.deactivate(),
            "KEY_UP":lambda: self.move_up(),
            "KEY_DOWN":lambda: self.move_down(),
            "KEY_KPENTER":lambda: self.flip_state(),
            "KEY_ENTER":lambda: self.flip_state()
            }
        self.keymap = keymap

    def set_contents(self, contents):
        """Sets the checkbox contents, as well as additionally re-sets ``last`` & ``first_displayed_entry`` pointers and calculates the value for ``last_displayed_entry`` pointer."""
        self.contents = contents
        self.process_contents(self.contents)
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

    def process_contents(self, contents):
        """Processes contents for custom callbacks. Currently, only 'exit' calbacks are supported.

        If ``self.append_exit`` is set, it goes through the menu and removes every callback which either is ``self.deactivate`` or is just a string 'exit'. 
        |Then, it appends a single ["Exit", '', 'exit'] element at the end of checkbox contents. It makes dynamically appending elements to checkbox easier and makes sure there's only one "Exit" callback, at the bottom of the checkbox."""
        self._contents = contents
        self.states = [element[2] if len(element)>1 else self.default_state for element in copy(self._contents)]
        self._contents.append([self.final_button_name, '', 'exit'])
        self.states.append(False) #For the final button, to maintain "len(states) == len(self._contents)"
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
            return ["No checkbox entries"]
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
            displayed_entry = self.render_displayed_entry(entry_num, checked = self.states[entry_num])
            displayed_data += displayed_entry
        #print("Displayed data: {}".format(displayed_data))
        return displayed_data

    def render_displayed_entry(self, entry_num, checked=False):
        """Renders a checkbox element by its position number in self._contents, determined also by display width, self.entry_height and element's representation type.
        If element's representation is a string, splits it into parts as long as the display's width in characters.
           If active flag is set, appends a "*" as the first entry's character. Otherwise, appends " ".
           TODO: omit " " and "*" if element height matches the display's row count.
        If element's representation is a list, it returns that list as the rendered entry, trimming its elements down or padding the list with empty strings to match the element's height as defined.
        """
        rendered_entry = []
        entry_content = self._contents[entry_num][0]
        display_columns = self.o.cols
        if type(entry_content) in [str, unicode]:
            if checked:
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
            if checked:
                entry_content[0][0] == "*"
            else:
                entry_content[0][0] == "*"
            while len(entry_content) < self.entry_height: #Can't have less either, padding with empty strings if necessary
                entry_content.append('')
            return entry_content
        else:
            raise Exception("Entries may contain either strings or lists of strings as their representations")
        #print("Rendered entry: {}".format(rendered_entry))
        return rendered_entry

    @to_be_foreground
    def refresh(self):
        logging.debug("{0}: refreshed data on display".format(self.name))
        displayed_data = self.get_displayed_data()
        active_line_num = (self.pointer - self.first_displayed_entry)*self.entry_height
        self.o.setCursor(active_line_num, 0)
        self.o.display_data(*displayed_data)
