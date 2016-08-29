from time import sleep
from copy import copy
import logging

from printer import Printer
from menu import Menu, to_be_foreground

class Listbox(Menu):
    """Implements a listbox to choose one thing from many.

    Attributes:

    * ``contents``: list of listbox elements
       
      Listbox element is a list, where:
         * ``element[0]`` (element's representation) is either a string, which simply has the element's value as it'll be displayed, such as "Menu element 1", or, in case of entry_height > 1, can be a list of strings, each of which represents a corresponding display row occupied by the element.
         * ``element[1]`` (element's value) is the value to be returned when element is selected.

      *If you want to set contents after the initalisation, please, use set_contents() method.*
    * ``pointer``: currently selected element's number in ``self.contents``.
    * ``in_foreground`` : a flag which indicates if listbox is currently displayed. If it's not set, inhibits any of listboxes actions which can interfere with other UI element being displayed.

    """
    contents = []
    _contents = []
    pointer = 0
    in_foreground = False
    exit_flag = False
    name = ""
    exitable = True
    selected_element = None

    def __init__(self, contents, i, o, name="Listbox", entry_height=1, append_exit=True):
        """Initialises the Listbox object.
        
        Args:

            * ``contents``: listbox contents
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``name``: listbox name which can be used internally and for debugging.
            * ``entry_height``: number of display rows one listbox element occupies.
            * ``append_exit``: appends an "Exit" element to listbox.

        """
        self.i = i
        self.o = o
        self.entry_height = entry_height
        self.name = name
        self.append_exit = append_exit
        self.set_contents(contents)
        self.generate_keymap()

    def to_foreground(self):
        """ Is called when listboxes ``activate()`` method is used, sets flags and performs all the actions so that menu can display its contents and receive keypresses. Also, updates the output device with rendered currently displayed menu elements."""
        logging.info("{0} enabled".format(self.name))    
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        """ A method which is called when listbox needs to start operating. Is blocking, sets up input&output devices, renders the listbox and waits until self.in_foreground is False, while menu callbacks are executed from the input device thread."""
        logging.info("{0} activated".format(self.name))    
        self.to_foreground() 
        if len(self.contents) == 0:
            Printer(["Nothing to", "choose from"], i, o)
            return None
        while self.in_foreground: #All the work is done in input callbacks
            sleep(0.1)
        logging.debug(self.name+" exited")
        if self.selected_element is None:
            return None
        return self.contents[self.selected_element][1]

    def deactivate(self):
        """ Deactivates the listbox completely, exiting it. As for now, pointer state is preserved through menu activations/deactivations """
        self.in_foreground = False
        logging.info("{0} deactivated".format(self.name))    

    @to_be_foreground
    def select_element(self):
        """ Gets the currently specified element's index and sets it as selected_element attribute.
        |Is typically used as a callback from input event processing thread."""
        logging.debug("element selected")
        self.selected_element = self.pointer
        self.deactivate()

    def process_contents(self):
        """Processes contents for custom callbacks. Currently, only 'exit' calbacks are supported.

        If ``self.append_exit`` is set, it goes through the menu and removes every callback which either is ``self.deactivate`` or is just a string 'exit'. 
        |Then, it appends a single ["Exit", 'exit'] element at the end of menu contents. It makes dynamically appending elements to menu easier and makes sure there's only one "Exit" callback, at the bottom of the menu."""
        if self.append_exit: 
            self.contents.append(["Exit", None])
        self._contents = self.contents #HAAAAAAAAAAAAAAX
        logging.debug("{}: listbox contents processed".format(self.name))
