from time import sleep
from helpers import setup_logger
logger = setup_logger(__name__, "warning")

import string

from ui.utils import to_be_foreground


class CharArrowKeysInput():
    """Implements a character input dialog which allows to input a character string using arrow keys to scroll through characters

    Attributes:

    * ``value``: A list of characters of the currently displayed value
    * ``position``: Position of the currently edited character.
    * ``cancel_flag``: A flag that is set when editing is cancelled.
    * ``in_foreground``: A flag which indicates if UI element is currently displayed. If it's not active, inhibits any of element's actions which can interfere with other UI element being displayed.
    * ``charmap``: Internal string that contains all of the possible character values
    * ``char_indices``: A list containing char's index in ``charmap`` for every char in ``value`` list
    * ``first_displayed_char``: An integer pointer to the first character currently displayed (for the occasions where part of value is off-screen)
    * ``last_displayed_char``: An integer pointer to the last character currently displayed

    """
    
    chars = string.ascii_lowercase
    Chars = string.ascii_uppercase
    numbers = '0123456789'
    hexadecimals = '0123456789ABCDEF'
    specials = "!\"#$%&'()[]<>*+,-./:;=?^_|"
    space = ' '
    backspace = chr(0x08)
     
    mapping = {
    '][c':chars,
    '][C':Chars,
    '][n':numbers,
    '][S':space,
    '][b':backspace,
    '][h':hexadecimals,
    '][s':specials}

    in_foreground = False
    value = []
    position = 0
    cancel_flag = False
    charmap = ""
    last_displayed_char = 0
    first_displayed_char = 0

    def __init__(self, i, o, message="Value:", value="",  allowed_chars=["][S", "][c", "][C", "][s", "][n"], name="CharArrowKeysInput", initial_value=""):
        """Initialises the CharArrowKeysInput object.
        
        Args:

            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``value``: Value to be edited. If not set, will start with an empty string.
            * ``allowed_chars``: Characters to be used during input. Is a list of strings designating ranges which can be the following:
              * '][c' for lowercase ASCII characters
              * '][C' for uppercase ASCII characters
              * '][s' for special characters from those supported by HD44780 character maps
              * '][S' for space
              * '][n' for numbers
              * '][h' for hexadecimal characters (0-F)
              If a string does not designate a range of characters, it'll be added to character map as-is.
            * ``message``: Message to be shown in the first row of the display
            * ``name``: UI element name which can be used internally and for debugging.

        """
        self.i = i
        self.o = o
        self.screen_cols = self.o.cols
        self.last_displayed_char = self.screen_cols
        self.message = message
        self.name = name
        self.generate_keymap()
        self.allowed_chars = allowed_chars
        self.allowed_chars.append("][b")
        self.generate_charmap()
        #Support for obsolete attribute
        if not value and initial_value:
            valuye = initial_value
        if type(value) != str:
            raise ValueError("CharArrowKeysInput needs a string!")
        self.value = list(value)
        self.char_indices = [] #Fixes a bug with char_indices remaining from previous input ( 0_0 )
        for char in self.value:
            self.char_indices.append(self.charmap.index(char))

    def to_foreground(self):
        """ Is called when ``activate()`` method is used, sets flags and performs all the actions so that UI element can display its contents and receive keypresses. Also, refreshes the screen."""
        logger.info("{0} enabled".format(self.name))    
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        """ A method which is called when input element needs to start operating. Is blocking, sets up input&output devices, renders the element and waits until self.in_background is False, while menu callbacks are executed from the input device thread.
        This method returns the selected value if KEY_ENTER was pressed, thus accepting the selection.
        This method returns None when the UI element was exited by KEY_LEFT and thus the value was not accepted. """
        logger.info("{0} activated".format(self.name))    
        self.o.cursor()
        self.to_foreground() 
        while self.in_foreground: #All the work is done in input callbacks
            sleep(0.1)
        self.o.noCursor()
        logger.debug(self.name+" exited")
        if self.cancel_flag:
            return None
        else:
            return ''.join(self.value) #Making string from the list we have

    def deactivate(self):
        """ Deactivates the UI element, exiting it and thus making activate() return."""
        self.in_foreground = False
        logger.info("{0} deactivated".format(self.name))    

    def print_value(self):
        """ A debug method. Useful for hooking up to an input event so that you can see current value. """
        logger.info(self.value)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which UI element is currently processing input events. """
        logger.info("{0} active".format(self.name))    

    @to_be_foreground
    def move_up(self):
        """Changes the current character to the next character in the charmap"""
        while len(self.char_indices) <= self.position: 
            self.char_indices.append(0)
            self.value.append(self.charmap[0])

        char_index = self.char_indices[self.position]
        if char_index >= (len(self.charmap)-1):
            char_index = 0
        else:
            char_index += 1
        self.char_indices[self.position] = char_index
        self.value[self.position] = self.charmap[char_index]
        self.refresh()    

    @to_be_foreground
    def move_down(self):
        """Changes the current character to the previous character in the charmap"""
        while len(self.char_indices) <= self.position: 
            self.char_indices.append(0)
            self.value.append(self.charmap[0])
        char_index = self.char_indices[self.position]
        if char_index == 0:
            char_index = len(self.charmap) - 1
        else:
            char_index -= 1
        self.char_indices[self.position] = char_index
        self.value[self.position] = self.charmap[char_index]
        self.refresh()    

    @to_be_foreground
    def move_right(self):
        """Moves cursor to the next element. """
        self.check_for_backspace()
        self.position += 1
        if self.last_displayed_char < self.position: #Went too far to the part of the value that isn't currently displayed
            self.last_displayed_char = self.position
            self.first_displayed_char = self.position - self.screen_cols
        self.refresh()

    @to_be_foreground
    def move_left(self):
        """Moves cursor to the previous element. If first element is chosen, exits and makes the element return None."""
        self.check_for_backspace()
        if self.position == 0:
            self.exit()
            return
        self.position -= 1
        if self.first_displayed_char > self.position: #Went too far back to the part that's not currently displayed
            self.first_displayed_char = self.position
            self.last_displayed_char = self.position + self.screen_cols
        self.refresh()

    @to_be_foreground
    def accept_value(self):
        """Selects the currently active number value, making activate() return it."""
        self.check_for_backspace()
        logger.debug("Value accepted")
        self.deactivate()

    @to_be_foreground
    def exit(self):
        """Exits discarding all the changes to the value."""
        logger.debug("{} exited without changes".format(self.name))
        self.cancel_flag = True
        self.deactivate()

    def generate_keymap(self):
        self.keymap = {
        "KEY_RIGHT":lambda: self.move_right(),
        "KEY_UP":lambda: self.move_up(),
        "KEY_DOWN":lambda: self.move_down(),
        "KEY_LEFT":lambda: self.move_left(),
        "KEY_KPENTER":lambda: self.accept_value(),
        "KEY_ENTER":lambda: self.accept_value()
        }

    def generate_charmap(self):
        for value in self.allowed_chars:
            if value in self.mapping.keys():
                self.charmap += self.mapping[value]
            else:
                self.charmap += value

    @to_be_foreground
    def set_keymap(self):
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.listen()

    def check_for_backspace(self):
        for i, char_value in enumerate(self.value):
            if char_value == self.backspace:
                self.value.pop(i)
                self.char_indices.pop(i)

    def get_displayed_data(self):
        """Formats the value and the message to show it on the screen, then returns a list that can be directly used by o.display_data"""
        if self.first_displayed_char >= len(self.value): #Value is off-screen
            value = ""
        else:
            value = ''.join(self.value)[self.first_displayed_char:][:self.screen_cols]
            value = value.replace(self.backspace, chr(0x7f))
            value = value.replace(' ', chr(255)) #Displaying all spaces as black boxes
        return [self.message, value]

    @to_be_foreground
    def refresh(self):
        self.o.setCursor(1, self.position-self.first_displayed_char)
        self.o.display_data(*self.get_displayed_data())
        logger.debug("{}: refreshed data on display".format(self.name))
