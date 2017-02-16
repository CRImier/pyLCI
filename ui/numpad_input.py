from time import sleep
from math import ceil
import logging
from functools import wraps
from threading import Lock

def to_be_foreground(func): 
    #A safety check wrapper so that certain functions can't possibly be called 
    #if UI element is not the one active
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

def check_value_lock(func): 
    #A safety check wrapper so that there's no race conditions between functions able to change position/value
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        #Value-changing code likely to run in concurrent thread and therefore we need a lock
        #if self.__locked_name__ is not None: print("Another function already locked the thread! Name is {}, current is {}".format(self.__locked_name__, func.__name__))
        self.value_lock.acquire()
        #self.__locked_name__ = func.__name__
        #print("Locked function {}".format(func.__name__))
        result = func(self, *args, **kwargs)
        self.value_lock.release()
        #print("Unlocked function {}".format(func.__name__))
        #self.__locked_name__ = None
        return result
    return wrapper

def check_position_overflow(condition):
    """Returns a decorator which can check for different ways of "self.position" counter overflow """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            #First, different checks depending on the type of check requested
            if condition == ">":
                overflow = self.position > len(self.value) # The biggest difference should be 1 character - for when position has advanced, but no character has been input
                difference = (len(self.value) - self.position) + 1
            elif condition == ">=":
                overflow = self.position >= len(self.value) #Can't be any positive difference, when updating the position pointer should be on an existing character
                difference = len(self.value) - self.position
            #Taking action if overflow happened
            if overflow:
                #TODO: insert proper logging
                #Fixing the overflow by adding space characters
                for _ in range(difference):
                    value.append(" ")
            #Checks done, executing decorated function
            result = func(self, *args, **kwargs)
            return result
        return wrapper
    return decorator


class NumpadCharInput():
    """Implements a character input UI element for a numeric keypad, allowing to translate numbers into characters.

    Attributes:

    * ``value``: currently entered number string.
    * ``in_foreground``: A flag which indicates if UI element is currently displayed. If it's not active, inhibits any of element's actions which can interfere with other UI element being displayed.

    """
    
    mapping = {"1":"1!",
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
    value_lock = None
    pending_character = None
    pending_counter = 0 
    pending_counter_start = 10 #Multiples of 0.1 second interval
    current_letter_num = 0
    __locked_name__ = None

    def __init__(self, i, o, message="", value="", name="NumpadCharInput", debug=False):
        """Initialises the NumpadCharInput object.
        
        Args:

            * ``i``, ``o``: input&output device objects

        """
        self.i = i
        self.o = o
        self.message = message
        self.name = name
        self.debug = debug
        self.value = value
        self.position = len(self.value)
        self.keymap = {}
        self.generate_keymap()
        self.value_lock = Lock()
        self.value_accepted = False

    #Default set of UI element functions - 

    def to_foreground(self):
        """ Is called when ``activate()`` method is used, sets flags and performs all the actions so that UI element can display its contents and receive keypresses. Also, refreshes the screen."""
        logging.info("{0} enabled".format(self.name))    
        self.value_accepted = False
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        """ A method which is called when input element needs to start operating. Is blocking, sets up input&output devices, renders the element and waits until self.in_background is False, while menu callbacks are executed from the input device thread.
        This method returns the selected value if KEY_ENTER was pressed, thus accepting the selection.
        This method returns None when the UI element was exited by KEY_LEFT and thus the value was not accepted. """
        logging.info("{0} activated".format(self.name))    
        self.o.cursor()
        self.to_foreground() 
        while self.in_foreground: #Most of the work is done in input callbacks
            sleep(0.1)
            self.check_character_state()
        self.o.noCursor()
        self.i.remove_streaming()
        logging.debug(self.name+" exited")
        if self.value_accepted:
            return self.value
        else:
            return None

    def deactivate(self):
        """ Deactivates the UI element, exiting it and thus making activate() return."""
        self.in_foreground = False
        logging.info("{0} deactivated".format(self.name))    

    def accept_value(self):
        logging.info("{0}: accepted value".format(self.name))    
        self.value_accepted = True
        self.deactivate()

    #Functions processing user input.

    @check_value_lock
    def process_streaming_keycode(self, key_name, *args):
        #This function processes all keycodes that are not in the keymap - such as number keycodes
        header = "KEY_"
        key = key_name[len(header):]
        if self.debug: print("Received "+key_name)
        if key in self.mapping.keys():
            #It's one of the keys we can process
            #NO INSERT IN MIDDLE/START SUPPORT
            if self.pending_character is None: #Currently no key pending
                #The position should be updated by now
                #Starting with first letter in the mapping for current key
                self.current_letter_num = 0
                letter = self.mapping[key][0]
                self.insert_letter_in_value(letter)
                if len(self.mapping[key]) == 1:
                    #No other characters that could be entered by using "pending character" function
                    #Thus, just moving forward
                    self.position += 1
                    #pending_character is already None so "pending letter" mechanism is disabled
                else:
                    #Other letters possible for the key
                    #So, onto the "countdown before character accepted" mechanism
                    self.pending_character = key
                    #Starting the "time before the character is accepted" countdown
                    self.pending_counter = self.pending_counter_start
                    #Output things on display
            elif self.pending_character != key: #Currently another key pending
                #Advancing position and inserting a new letter
                self.position += 1
                #Starting with first letter in the mapping for current key
                self.current_letter_num = 0
                letter = self.mapping[key][0]
                self.insert_letter_in_value(letter)
                if len(self.mapping[key]) == 1:
                    #No other characters that could be entered 
                    #Thus, just setting pending_character to None
                    self.pending_character = None
                    #Need to move forward once again - cursor still points at the previous character
                    self.position += 1
                else:
                    #There are other characters possible for the new letter
                    #So, onto the "countdown before character accepted" mechanism
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

    @check_value_lock
    def backspace(self):
        self.remove_letter_in_value()
        self.refresh()

    #Functions that do processing on the current value

    @check_position_overflow(">")
    def insert_letter_in_value(self, letter):
        if self.position in range(len(self.value)):
            #Inserting character in the middle of the string
            value_before_letter = self.value[:self.position]
            value_after_letter = self.value[self.position:]
            self.value = "".join([value_before_letter, letter, value_after_letter])
        elif self.position == len(self.value): #Right on the last character
            self.value += letter
        else:
            import pdb;pdb.set_trace()

    @check_position_overflow(">=")
    def update_letter_in_value(self, letter):
        #Split the value string to list of characters, replace the letter and assemble the string again
        value_l = list(self.value)
        value_l[self.position] = letter
        self.value = "".join(value_l)

    @check_position_overflow(">")
    def remove_letter_in_value(self):
        if self.position == 0 and not self.value:
            #Nothing to be done
            return None
        elif self.position in [len(self.value)-1] and self.pending_character is not None:
            #Trying to remove the character which is currently pending
            self.pending_character = None
            self.value = self.value[:-1]
        elif self.position in range(len(self.value)):
            #Inserting character in the middle of the string
            value_before_letter = self.value[:self.position-1]
            value_after_letter = self.value[self.position:]
            self.value = "".join(value_before_letter, value_after_letter)
            self.position -= 1
        elif self.position == len(self.value): 
            #Just removing the last character
            self.value = self.value[:-1]
            self.position -= 1

    #Functions that work with "pending counter"

    @check_value_lock
    def check_character_state(self):
        if self.pending_character is not None:
            #Character still pending
            self.pending_counter -= 1
            if self.pending_counter == 0:
                #Counter reset
                self.pending_character = None
                #Advancing position so that next letter takes the next space
                self.position += 1 
                self.refresh()

    #Functions that set up the input listener

    def generate_keymap(self):
        self.keymap.update({
        "KEY_ENTER":lambda: self.accept_value(),
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
        lines_taken_by_value = (len(self.value) / (screen_cols)) + 1
        for line_i in range(lines_taken_by_value):
            displayed_data.append(self.value[(line_i*screen_cols):][:screen_cols])
        empty_line_count = screen_rows - (static_line_count + lines_taken_by_value)
        for _ in range(empty_line_count):
            displayed_data.append("") #Just empty line
        half_line_length = screen_cols/2
        last_line = "Cancel".center(half_line_length) + "Erase".center(half_line_length)
        displayed_data.append(last_line)
        return displayed_data

    @to_be_foreground
    def refresh(self):
        """Function that is called each time data has to be output on display"""
        cursor_y, cursor_x = divmod(self.position, self.o.cols)
        cursor_y += 1
        self.o.setCursor(cursor_y, cursor_x)
        self.o.display_data(*self.get_displayed_data())
        logging.debug("{}: refreshed data on display".format(self.name))

    #Debug-related functions.

    def print_value(self):
        """ A debug method. Useful for hooking up to an input event so that you can see current value. """
        logging.info(self.value)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that you can see which UI element is currently processing input events. """
        logging.info("{0} active".format(self.name))    



class NumpadNumberInput(NumpadCharInput):
    """Implements a number input UI element for a numeric keypad, allowing to translate number keys into numbers."""
    
    #Quite straightforward mapping for now
    mapping = {"1":"1",
               "2":"2",
               "3":"3",
               "4":"4",
               "5":"5",
               "6":"6",
               "7":"7",
               "8":"8",
               "9":"9",
               "0":"0",
               "*":"*",
               "#":"#"}
