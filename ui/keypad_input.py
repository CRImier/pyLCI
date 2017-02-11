from time import sleep
from math import ceil
import logging


def to_be_foreground(func): #A safety check wrapper so that certain checks don't get called if menu is not the one active
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

class NumericKeypadCharacterInput():
    """Implements a character input UI element for a numeric keypad, allowing to translate numbers into characters.

    Attributes:

    * ``value``: currently entered number string.
    * ``in_foreground``: A flag which indicates if UI element is currently displayed. If it's not active, inhibits any of element's actions which can interfere with other UI element being displayed.

    """
    
    mapping = {"1":"1",
               "2":"abcABC2",
               "3":"defDEF3",
               "4":"ghiGHI4",
               "5":"jklJKL5",
               "6":"mnoMNO6",
               "7":"pqrsPQRS7",
               "8":"tuvTUV8",
               "9":"wxyzWXYZ9",
               "0":" 0+",
               "*":"*",
               "#":"#"
              }
    
    in_foreground = False

    value = ""
    position = 0

    pending_character = None
    pending_counter = 0 
    pending_counter_start = 10 #Multiples of 0.1 second interval
    current_letter_num = 0

    def __init__(self, i, o, message=None, name="NumericKeypadCharacterInput"):
        """Initialises the NumericKeypadCharacterInput object.
        
        Args:

            * ``i``, ``o``: input&output device objects

        """
        self.i = i
        self.o = o
        self.message = message
        self.name = name
        self.generate_keymap()

    #Default set of UI element functions - 

    def to_foreground(self):
        """ Is called when ``activate()`` method is used, sets flags and performs all the actions so that UI element can display its contents and receive keypresses. Also, refreshes the screen."""
        logging.info("{0} enabled".format(self.name))    
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        """ A method which is called when input element needs to start operating. Is blocking, sets up input&output devices, renders the element and waits until self.in_background is False, while menu callbacks are executed from the input device thread.
        This method returns the selected value if KEY_ENTER was pressed, thus accepting the selection.
        This method returns None when the UI element was exited by KEY_LEFT and thus the value was not accepted. """
        logging.info("{0} activated".format(self.name))    
        self.to_foreground() 
        while self.in_foreground: #Most of the work is done in input callbacks
            sleep(0.1)
            self.check_character_state()
        self.i.remove_streaming()
        logging.debug(self.name+" exited")
        return self.value

    def deactivate(self):
        """ Deactivates the UI element, exiting it and thus making activate() return."""
        self.in_foreground = False
        logging.info("{0} deactivated".format(self.name))    

    #Functions processing user input.

    def process_streaming_keycode(self, key_name, *args):
        #This function processes all keycodes that are not in the keymap - such as number keycodes
        header = "KEY_"
        key = key_name[len(header):]
        if key in self.mapping.keys():
            #It's one of the keys we can process
            #NO INSERT IN MIDDLE/START SUPPORT
            if self.pending_character != key: #Currently no key or another key pending
                #Advancing position and inserting a new letter
                self.position += 1
                #Starting with first letter in the mapping for current key
                self.current_letter_num = 0
                letter = self.mapping[key][0]
                self.insert_letter_in_value(letter)
                #Now onto the "countdown before character accepted" mechanism
                self.pending_character = key
                #Starting the "time before the character is accepted" countdown
                self.pending_counter = self.pending_counter_start
                #Output things on display
            elif self.pending_character == key: #Current pending key is the same as the one pressed
                #Just updating the value and resetting the countdown
                self.current_letter_num += 1
                #Wrapping around in case of overflow
                if self.current_letter_num not in range(len(self.mapping[key])):
                    self.current_letter_num = 0
                letter = self.mapping[key][self.current_letter_num]
                #Replacing the current character
                self.update_letter_in_value(letter)
                #For fast typists, not resetting the counter could be an option in the future
                #That'd mean there'd be only 1 second in total to choose from all letters, so it needs to be tested
                self.pending_counter = self.pending_counter_start
            #Finally, output all changes to display
            self.refresh()

    def backspace(self):
        self.value = self.value[:-1]
        self.refresh()

    #Functions that do processing on the current value

    def insert_letter_in_value(self, letter):
        #First, check if there isn't position counter overflow
        if self.position > len(self.value)+1: # The biggest difference should be 1 character - for when position has advanced, but no character yet has been input
            print(self.name+": WTF, position counter overflow")
            #Fixing the overflow by adding space characters
            difference = (len(self.value)+1) - self.position
            for _ in range(difference):
                value.append(" ")
        if self.position in range(len(self.value)):
            #Inserting character in the middle of the string
            value_before_letter = self.value[:self.position]
            value_after_letter = self.value[self.position:]
            self.value = "".join(value_before_letter, letter, value_after_letter)
        elif self.position == len(self.value): #Right on the last character
            self.value += self.letter

    def update_letter_in_value(self, letter):
        #First, check if there isn't position counter overflow (I know, I know, would do better as a decorator)
        if self.position >= len(self.value): #Can't be any positive difference, when updating the position pointer should be on an existing character
            print(self.name+": WTF, position counter overflow")
            #Fixing the overflow by adding space characters
            difference = (len(self.value)) - self.position
            for _ in range(difference):
                value.append(" ")
        #yeah, this simple.
        self.value[self.position] = letter

    #Functions that check the counter state and act accordingly

    

    #Functions that set up the input listener

    def generate_keymap(self):
        self.keymap.update({
        "KEY_F1":lambda: self.deactivate(),
        "KEY_F2":lambda: self.backspace()
        })

    @to_be_foreground
    def set_keymap(self):
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.set_streaming(self.process_streaming_keycode)
        self.i.listen()

    #Functions that are responsible for input to display

    def get_displayed_data(self):
        """Experimental: not meant for 2x16 displays
        
        Formats the value and the message to show it on the screen, then returns a list that can be directly used by o.display_data"""
        displayed_data = [self.message]
        screen_rows = self.o.rows
        screen_cols = self.o.cols
        static_line_count = 2 #One for message, another for context key labels
        lines_taken_by_value = int(ceil( float(len(self.value)) / (screen_rows-static_line_count) ))
        for line_i in range(lines_taken_by_value):
            displayed_data.append(self.value[(line_i*screen_cols):][:screen_cols])
        for _ in range( screen_rows - (static_line_count + lines_taken_by_value) ):
            displayed_data.append("") #Just empty line
        half_line_length = screen_cols/2
        last_line = "Cancel".center(half_line_length) + "Erase".center(half_line_length)
        displayed_data.append(last_line)
        print(displayed_data)
        return displayed_data

    @to_be_foreground
    def refresh(self):
        """Function that is called each time data has to be output on display"""
        self.o.display_data(*self.get_displayed_data())
        logging.debug("{}: refreshed data on display".format(self.name))

    #Debug-related functions.

    def print_value(self):
        """ A debug method. Useful for hooking up to an input event so that you can see current value. """
        logging.info(self.value)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which UI element is currently processing input events. """
        logging.info("{0} active".format(self.name))    

