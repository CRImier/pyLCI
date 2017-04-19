"""Contains base classes for UI elements that consist of entries, that can be scrolled through using arrow keys.
Best example of such an element is a Menu element - which has menu entries you can scroll through, which execute a callback when you click on them. """

import logging
from copy import copy
from time import sleep
from threading import Event

def to_be_foreground(func):
    """A safety check wrapper so that certain checks don't get called if UI element is
       not the one active"""

    def wrapper(self, *args, **kwargs):
        if self.in_foreground:
            return func(self, *args, **kwargs)
        else:
            return False
    return wrapper

class BaseListUIElement():
    """This is a base UI element for list-like UI elements."""

    contents = []
    pointer = 0
    in_foreground = False
    name = ""
    first_displayed_entry = 0
    last_displayed_entry = None
    exit_entry = ["Exit", "exit"]

    def __init__(self, contents, i, o, name=None, entry_height=1, append_exit=True, exitable=True, scrolling=True, keymap=None):
        self.i = i
        self.o = o
        self.entry_height = entry_height
        self.keymap = keymap if keymap else {}
        self.name = name
        self.append_exit = append_exit
        self.exitable = exitable
        self.scrolling={"enabled":scrolling,
                        "current_finished":False,
                        "current_scrollable":False,
                        "counter":0,
                        "pointer":0}
        self.set_contents(contents)
        self.generate_keymap()

    def before_foreground(self):
        """Hook for child UI elements"""
        pass

    def to_foreground(self):
        """ Is called when UI element's ``activate()`` method is used, sets flags
            and performs all the actions so that UI element can display its contents
            and receive keypresses. Also, refreshes the screen."""
        logging.info("{0} enabled".format(self.name))
        self.before_foreground()
        self.reset_scrolling()
        self.in_foreground = True
        self.o.cursor()
        self.refresh()
        self.set_keymap()

    def idle_loop(self):
        """Contains code which will be executed in UI element's idle loop """
        sleep(0.1)
        self.scroll()

    def activate(self):
        """ A method which is called when UI element needs to start operating.
            Is blocking, sets up input&output devices, renders the UI element and
            waits until self.in_foreground is False, while UI element callbacks
            are executed from the input listener thread."""
        logging.info("{0} activated".format(self.name))
        self.to_foreground()
        while self.in_foreground: #All the work is done in input callbacks
            self.idle_loop()
        return_value = self.get_return_value()
        logging.info("{} exited".format(self.name))
        return return_value

    def get_return_value(self):
        """To be overridden by child UI elements. Return value will be returned when
           UI element's ``activate()`` exits."""
        return None #Default value to indicate that no meaningful result was returned

    def deactivate(self):
        """Sets a flag that signals the UI element's ``activate()`` to return."""
        self.in_foreground = False
        self.o.noCursor()
        logging.info("{} deactivated".format(self.name))

    @to_be_foreground
    def scroll(self):
        if self.scrolling["enabled"] and not self.scrolling["current_finished"] and self.scrolling["current_scrollable"]:
            self.scrolling["counter"] += 1
            if self.scrolling["counter"] == 10:
                self.scrolling["pointer"] += 1
                self.scrolling["counter"] = 0
                self.refresh()

    def reset_scrolling(self):
        self.scrolling["current_finished"] = False
        self.scrolling["pointer"] = 0
        self.scrolling["counter"] = 0

    def print_contents(self):
        """ A debug method. Useful for hooking up to an input event so that
            you can see the representation of current UI element's contents. """
        logging.info(self.contents)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that
            you can see which UI element is currently processing input events. """
        logging.info("Active UI element is {0}".format(self.name))

    def get_entry_count_per_screen(self):
        return self.o.rows / self.entry_height

    @to_be_foreground
    def move_down(self):
        """ Moves the pointer one entry down, if possible.
        |Is typically used as a callback from input event processing thread.
        |TODO: support going from bottom to top when pressing "down" with
        last entry selected."""
        if self.pointer < (len(self.contents)-1):
            logging.debug("moved down")
            self.pointer += 1
            self.reset_scrolling()
            self.refresh()
            return True
        else:
            return False

    @to_be_foreground
    def page_down(self):
        """ Scrolls up a full screen of entries, if possible.
            If not possible, moves as far as it can."""
        counter = self.get_entry_count_per_screen()
        while counter != 0 and self.pointer < (len(self.contents)-1):
            logging.debug("moved down")
            self.pointer += 1
            counter -= 1
        self.refresh()
        self.reset_scrolling()
        return True

    @to_be_foreground
    def move_up(self):
        """ Moves the pointer one entry up, if possible.
        |Is typically used as a callback from input event processing thread.
        |TODO: support going from top to bottom when pressing "up" with
        first entry selected."""
        if self.pointer != 0:
            logging.debug("moved up")
            self.pointer -= 1
            self.refresh()
            self.reset_scrolling()
            return True
        else:
            return False

    @to_be_foreground
    def page_up(self):
        """ Scrolls down a full screen of UI entries, if possible.
            If not possible, moves as far as it can."""
        counter = self.get_entry_count_per_screen()
        while counter != 0 and self.pointer != 0:
            logging.debug("moved down")
            self.pointer -= 1
            counter -= 1
        self.refresh()
        self.reset_scrolling()
        return True

    @to_be_foreground
    def select_entry(self):
        """To be overridden by child UI elements. Is executed when ENTER is pressed
           in UI element."""
        print(self.contents[self.pointer])

    def generate_keymap(self):
        """Makes the keymap dictionary for the input device."""
        self.keymap.update({
            "KEY_UP":lambda: self.move_up(),
            "KEY_DOWN":lambda: self.move_down(),
            "KEY_PAGEUP":lambda: self.page_up(),
            "KEY_PAGEDOWN":lambda: self.page_down(),
            "KEY_KPENTER":lambda: self.select_entry(),
            "KEY_ENTER":lambda: self.select_entry()
            })
        if self.exitable:
            self.keymap["KEY_LEFT"] = lambda: self.deactivate()

    def set_contents(self, contents):
        """Sets the UI element contents and triggers pointer recalculation."""
        self.validate_contents(contents)
        self.contents = contents
        self.process_contents()
        self.fix_pointers_on_contents_update()

    def validate_contents(self, contents):
        #if not contents:
        #    raise ValueError("UI element 'contents' argument has to be set to a non-empty list!")
        for entry in contents:
            entry_repr = entry[0]
            if not isinstance(entry_repr, str) and not isinstance(entry_repr, list):
                raise Exception("Entries can be either strings or lists of strings - {} is neither!".format(entry))
            if isinstance(entry_repr, list):
                for entry_str in entry_repr:
                    if not isinstance(entry_str, str):
                        raise Exception("List entries can only contain strings - {} is not a string!".format(entry_str))

    def fix_pointers_on_contents_update(self):
        """Boundary-checks ``pointer``, re-sets ``last`` & ``first_displayed_entry`` pointers
           and calculates the value for ``last_displayed_entry`` pointer."""
        if  self.pointer > len(self.contents)-1:
            #Pointer went too far, setting it to last entry position
            self.pointer = len(self.contents) - 1
        full_entries_shown = self.get_entry_count_per_screen()
        entry_count = len(self.contents)
        self.first_displayed_entry = 0
        if full_entries_shown > entry_count: #Display is capable of showing more entries than we have, so the last displayed entry is the last menu entry
            logging.debug("There are more display rows than entries can take, correcting")
            self.last_displayed_entry = entry_count-1
        else:
            logging.debug("There are no empty spaces on the display")
            self.last_displayed_entry = full_entries_shown-1 #We start numbering entries with 0, so 4-row screen would show entries 0-3
        logging.debug("First displayed entry is {}".format(self.first_displayed_entry))
        logging.debug("Last displayed entry is {}".format(self.last_displayed_entry))

    def process_contents(self):
        """Processes contents for custom callbacks. Currently, only 'exit' calbacks are supported.

        If ``self.append_exit`` is set, it goes through the menu and removes every callback which either is ``self.deactivate`` or is just a string 'exit'. 
        |Then, it appends a single "Exit" entry at the end of menu contents. It makes dynamically appending entries to menu easier and makes sure there's only one "Exit" callback, at the bottom of the menu."""
        if self.append_exit:
            #filtering possible duplicate exit entries
            while self.exit_entry in self.contents:
                self.contents.remove(self.exit_entry)
            self.contents.append(self.exit_entry)
        logging.debug("{}: contents processed".format(self.name))

    @to_be_foreground
    def set_keymap(self):
        """Sets the input device's keycode-to-callback mapping. Re-starts the input device because ofpassing-variables-between-threads issues."""
        self.i.stop_listen()
        self.i.set_keymap(self.keymap)
        self.i.listen()

    def fix_pointers_on_refresh(self):
        if self.pointer < self.first_displayed_entry:
            logging.debug("Pointer went too far to top, correcting")
            self.last_displayed_entry -=  self.first_displayed_entry - self.pointer #The difference will mostly be 1 but I guess it might be more in case of concurrency issues
            self.first_displayed_entry = self.pointer
        if self.pointer > self.last_displayed_entry:
            logging.debug("Pointer went too far to bottom, correcting")
            self.first_displayed_entry += self.pointer - self.last_displayed_entry
            self.last_displayed_entry = self.pointer
        logging.debug("First displayed entry is {}".format(self.first_displayed_entry))
        logging.debug("Last displayed entry is {}".format(self.last_displayed_entry))

    def get_displayed_data(self):
        """Generates the displayed data in a way that the output device accepts. The output of this function can be fed in the o.display_data function.
        |Corrects last&first_displayed_entry pointers if necessary, then gets the currently displayed entries' numbers, renders each one of them and concatenates them into one big list which it returns.
        |Doesn't support partly-rendering entries yet."""
        displayed_data = []
        disp_entry_positions = range(self.first_displayed_entry, self.last_displayed_entry+1)
        #print("Displayed entries: {}".format(disp_entry_positions))
        for entry_num in disp_entry_positions:
            is_active = entry_num == self.pointer
            displayed_entry = self.render_displayed_entry(entry_num, active=is_active)
            displayed_data += displayed_entry
        #print("Displayed data: {}".format(displayed_data))
        return displayed_data

    def render_displayed_entry(self, entry_num, active=False):
        """Renders an UI element entry by its position number in self.contents, determined also by display width, self.entry_height and entry's representation type.
        If entry representation is a string, splits it into parts as long as the display's width in characters.
           If active flag is set, appends a "*" as the first entry's character. Otherwise, appends " ".
           TODO: omit " " and "*" if entry height matches the display's row count.
        If entry representation is a list, it returns that list as the rendered entry, trimming and padding with empty strings when necessary (to match the ``entry_height``).
        """
        rendered_entry = []
        entry = self.contents[entry_num][0]
        display_columns = self.o.cols
        if type(entry) in [str, unicode]:
            if active:
                #Scrolling only works with strings for now
                avail_display_chars = (self.o.cols*self.entry_height)-1 #1 char for "*"/" "
                self.scrolling["current_scrollable"] = len(entry) > avail_display_chars
                self.scrolling["current_finished"] = len(entry)-self.scrolling["pointer"] < avail_display_chars
                if self.scrolling["current_scrollable"] and not self.scrolling["current_finished"]:
                    entry = entry[self.scrolling["pointer"]:]
                rendered_entry.append(entry[:display_columns-1]) #First part of string displayed
                entry = entry[display_columns-1:] #Shifting through the part we just displayed
            else:
                rendered_entry.append(entry[:display_columns-1])
                entry = entry[display_columns-1:]
            for row_num in range(self.entry_height-1): #First part of string done, if there are more rows to display, we give them the remains of string
                rendered_entry.append(entry[:display_columns])
                entry = entry[display_columns:]
        elif type(entry) == list:
            entry = entry[:self.entry_height] #Can't have more arguments in the list argument than maximum entry height
            while len(entry) < self.entry_height: #Can't have less either, padding with empty strings if necessary
                entry.append('')
            return [str(entry_str)[:o.cols] for entry_str in entry]
        else:
            #How did this slip past the check on set_contents?
            raise Exception("Entries may contain either strings or lists of strings as their representations")
        logging.debug("Rendered entry: {}".format(rendered_entry))
        return rendered_entry

    @to_be_foreground
    def refresh(self):
        logging.debug("{}: refreshed data on display".format(self.name))
        self.fix_pointers_on_refresh()
        displayed_data = self.get_displayed_data()
        active_line_num = (self.pointer - self.first_displayed_entry)*self.entry_height
        #Workaround for current state of graphical display library
        #Not going to work on HD44780-based screens, lines need to be reordered
        self.o.setCursor(active_line_num, 0)
        self.o.cursor()
        self.o.display_data(*displayed_data)


class BaseListBackgroundableUIElement(BaseListUIElement):
    """This is a base UI element for list-like UI elements.
       This UI element has the ability to go into background. It's usually for the cases when
       an UI element can call another UI element, after the second UI element returns,
       context has to return to the first UI element - like in nested menus.
       This UI element also has built-in scrolling of entries - if the entry text is longer
       than the screen, once the entry is selected, UI element will scroll through its text."""

    def __init__(self, *args, **kwargs):
        self._in_background = Event()
        BaseListUIElement.__init__(self, *args, **kwargs)

    @property
    def in_background(self):
        return self._in_background.isSet()

    @in_background.setter
    def in_background(self, value):
        if value == True:
            self._in_background.set()
        elif value == False:
            self._in_background.clear()

    def to_foreground(self):
        """ Is called when UI element's ``activate()`` method is used, sets flags
            and performs all the actions so that UI element can display its contents
            and receive keypresses. Also, refreshes the screen."""
        self.in_background = True
        BaseListUIElement.to_foreground(self)

    @to_be_foreground
    def to_background(self):
        """ Inhibits all UI element's refreshes, effectively bringing it to background."""
        self.o.noCursor()
        self.in_foreground = False
        logging.info("{0} disabled".format(self.name))

    def activate(self):
        """ A method which is called when UI element needs to start operating.
            Is blocking, sets up input&output devices, renders the UI element and
            waits until self.in_background is False, while UI element callbacks
            are executed from the input listener thread."""
        logging.info("{0} activated".format(self.name))
        self.to_foreground()
        while self.in_background: #All the work is done in input callbacks
            self.idle_loop()
        return_value = self.get_return_value()
        logging.info("{} exited".format(self.name))
        return return_value

    def deactivate(self):
        """Sets a flag that signals the UI element's ``activate()`` to return."""
        self.in_background = False
        BaseListUIElement.deactivate(self)
