from time import sleep
from helpers import setup_logger

from luma.core.render import canvas as luma_canvas
from utils import invert_rect_colors

logger = setup_logger(__name__, "info")

class DialogBox(object):
    """Implements a dialog box with given values (or some default ones if chosen)."""

    value_selected = False
    selected_option = 0
    default_options = {"y":["Yes", True], 'n':["No", False], 'c':["Cancel", None]}

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
        if isinstance(values, basestring):
            self.values = []
            for char in values:
                self.values.append(self.default_options[char])
            #value_str = " ".join([value[0] for value in values])
            #assert(len(value_str) <= o.cols, "Resulting string too long for the display!")
        else:
            if not type(values) in (list, tuple):
                raise ValueError("Unsupported 'values' argument - needs a list, supplied {}".format(repr(values)))
            if not values:
                raise ValueError("Empty/invalid 'values' argument!")
            for i, value in enumerate(values):
                if isinstance(value, basestring) and value in self.default_options:
                    #"y", "n" or "c" supplied as a shorthand for one of three default arguments
                    values[i] = self.default_options[value]
            self.values = values
        self.message = message
        self.generate_keymap()
        self.set_view()

    def to_foreground(self):
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def set_view(self):
        if "b&w-pixel" in self.o.type:
            view_class = GraphicalView
        elif "char" in self.o.type:
            view_class = TextView
        else:
            raise ValueError("Unsupported display type: {}".format(repr(self.o.type)))
        self.view = view_class(self.o, self)

    def activate(self):
        logger.debug("{0} activated".format(self.name))
        self.to_foreground() 
        self.value_selected = False
        self.selected_option = 0
        while self.in_foreground: #All the work is done in input callbacks
            self.idle_loop()
        logger.debug(self.name+" exited")
        if self.value_selected:
            return self.values[self.selected_option][1]
        else:
            return None

    def idle_loop(self):
        sleep(0.1)

    def deactivate(self):
        self.in_foreground = False
        logger.debug("{0} deactivated".format(self.name))

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
        if self.selected_option == 0:
            self.deactivate()
            return
        self.selected_option -= 1
        self.refresh()

    def move_right(self):
        if self.selected_option == len(self.values)-1:
            return
        self.selected_option += 1
        self.refresh()

    def accept_value(self):
        self.value_selected = True
        self.deactivate()

    def refresh(self):
        self.view.refresh()


class TextView():

    def __init__(self, o, el):
        self.o = o
        self.el = el
        self.process_values()

    def process_values(self):
        labels = [label for label, value in self.el.values]
        label_string = " ".join(labels)
        if len(label_string) > self.o.cols:
            raise ValueError("DialogBox {}: all values combined are longer than screen's width".format(self.name))
        self.right_offset = (self.o.cols - len(label_string))/2
        self.displayed_label = " "*self.right_offset+label_string
        #Need to go through the string to mark the first places because we need to remember where to put the cursors
        current_position = self.right_offset
        self.positions = []
        for label in labels:
            self.positions.append(current_position)
            current_position += len(label) + 1

    def refresh(self):
        self.o.noCursor()
        self.o.setCursor(1, self.positions[self.el.selected_option])
        self.o.display_data(self.el.message, self.displayed_label)
        self.o.cursor()


class GraphicalView(TextView):

    def get_image(self):
        draw = luma_canvas(self.o.device)
        d = draw.__enter__()

        #Drawing text
        second_line_position = 10
        d.text((2, 0), self.el.message, fill="white")
        d.text((2, second_line_position), self.displayed_label, fill="white")

        #Calculating the cursor dimensions
        first_char_position = self.positions[self.el.selected_option]
        option_length = len( self.el.values[self.el.selected_option][0] )
        c_x1 = first_char_position * self.o.char_width
        c_x2 = c_x1 + option_length * self.o.char_width
        c_y1 = second_line_position #second line
        c_y2 = c_y1 + self.o.char_height
        #Some readability adjustments
        cursor_dims = ( c_x1, c_y1, c_x2 + 2, c_y2 + 2 )

        #Drawing the cursor
        invert_rect_colors(cursor_dims, d, draw.image)

        return draw.image

    def refresh(self):
        self.o.display_image(self.get_image())
