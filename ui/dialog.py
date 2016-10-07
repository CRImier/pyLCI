from time import sleep
import logging

class DialogBox():
    """Implements a dialog box with given values (or some default ones if chosen)."""

    value_selected = False
    pointer = 0
    
    def __init__(self, values, i, o, message="Are you sure?", name="DialogBox"):
        """Initialises the DialogBox object.

        Args:

            * ``values``: values to be used. Should be a list of ``[label, returned_value]`` pairs.

              * You can also pass a string "yn" to get "Yes(True), No(False)" options, or "ync" to get "Yes(True), No(False), Cancel(None)" options.
              * Values put together with spaces between them shouldn't be longer than the screen's width.

            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``message``: Message to be shown on the first line of the screen when UI element is activated
            * ``name``: UI element name which can be used internally and for debugging.

        """
        self.i = i
        self.o = o
        self.name = name
        if values == 'yn':
            self.values = [["Yes", True], ["No", False]]
        elif values == 'ync':
            self.values = [["Yes", True], ["No", False], ["Cancel", None]]
        else:
            assert(type(values) in (list, tuple), "Unsupported 'values' argument!")
            assert(values, "DialogBox: Empty/invalid 'values' argument!")
            self.values = values
        self.message = message
        self.process_values()
        self.generate_keymap()

    def to_foreground(self):
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def activate(self):
        logging.info("{0} activated".format(self.name))    
        self.to_foreground() 
        self.value_selected = False
        self.pointer = 0
        self.o.cursor()
        while self.in_foreground: #All the work is done in input callbacks
            sleep(0.1)
        self.o.noCursor()
        logging.debug(self.name+" exited")
        if self.value_selected:
            return self.values[self.pointer][1]
        else:
            return None

    def deactivate(self):
        self.in_foreground = False
        logging.info("{0} deactivated".format(self.name))    

    def generate_keymap(self):
        self.keymap = {
        "KEY_RIGHT":lambda: self.move_right(),
        "KEY_LEFT":lambda: self.move_left(),
        "KEY_KPENTER":lambda: self.accept_value(),
        "KEY_ENTER":lambda: self.accept_value()
        }

    def set_keymap(self):
        self.i.stop_listen()
        self.i.clear_keymap()
        self.i.keymap = self.keymap
        self.i.listen()

    def move_left(self):
        if self.pointer == 0:
            self.deactivate()
            return
        self.pointer -= 1
        self.refresh()

    def move_right(self):
        if self.pointer == len(self.values)-1:
            return
        self.pointer += 1
        self.refresh()

    def accept_value(self):
        self.value_selected = True
        self.deactivate()

    def process_values(self):
        self.labels = [label for label, value in self.values]
        label_string = " ".join(self.labels)
        if len(label_string) > self.o.cols:
            raise ValueError("DialogBox {}: all values combined are longer than screen's width".format(self.name))
        self.right_offset = (self.o.cols - len(label_string))/2
        self.displayed_label = " "*self.right_offset+label_string
        #Need to go through the string to mark the first places because we need to remember where to put the cursors
        current_position = self.right_offset
        self.positions = []
        for label in self.labels:
            self.positions.append(current_position)
            current_position += len(label) + 1

    def refresh(self):
        self.o.noCursor()
        self.o.display_data(self.message, self.displayed_label)
        self.o.cursor()
        self.o.setCursor(1, self.positions[self.pointer])
