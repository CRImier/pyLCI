"""Contains base classes for UI elements that deal with lists of entries, that can be scrolled through using arrow keys.
Best example of such an element is a Menu element - it has menu entries you can scroll through, which execute a callback
 when you click on them. """

from copy import copy
from threading import Event
from time import sleep

from canvas import Canvas
from helpers import setup_logger
from utils import to_be_foreground, clamp_list_index


logger = setup_logger(__name__, "warning")

global_config = {}

# Documentation building process has problems with this import
try:
    import ui.config_manager as config_manager
except (ImportError, AttributeError):
    pass
else:
    cm = config_manager.get_ui_config_manager()
    cm.set_path("ui/configs")
    try:
        global_config = cm.get_global_config()
    except OSError as e:
        logger.error("Config files not available, running under ReadTheDocs?")
        logger.exception(e)


class BaseListUIElement(object):
    """This is a base UI element for list-like UI elements.

       This UI element has built-in scrolling of entries - if the entry text is longer
       than the screen, once the entry is selected, UI element will scroll through its text."""

    contents = []
    pointer = 0
    start_pointer = 0
    in_foreground = False
    name = ""
    exit_entry = ["Back", "exit"]

    config_key = "base_list_ui"

    def __init__(self, contents, i, o, name=None, entry_height=1, append_exit=True, exitable=True, scrolling=True,
                 config=None, keymap=None):
        self.i = i
        self.o = o
        self.entry_height = entry_height
        self.keymap = keymap if keymap else {}
        self.name = name
        self.append_exit = append_exit
        self.exitable = exitable
        self.scrolling = {
            "enabled": scrolling,
            "current_finished": False,
            "current_scrollable": False,
            "counter": 0,
            "pointer": 0
        }
        self.config = config if config is not None else global_config
        self.set_view(self.config.get(self.config_key, {}))
        self.set_contents(contents)
        self.generate_keymap()

    def set_views_dict(self):
        self.views = {
            "TextView": TextView,
            "EightPtView": EightPtView,
            "SixteenPtView": SixteenPtView,
            "MainMenuTripletView": MainMenuTripletView,
            "PrettyGraphicalView": SixteenPtView,  # Not a descriptive name - left for compatibility
            "SimpleGraphicalView": EightPtView  # Not a descriptive name - left for compatibility
        }

    def set_view(self, config):
        view = None
        self.set_views_dict()
        if self.name in config.get("custom_views", {}).keys():
            view_config = config["custom_views"][self.name]
            if isinstance(view_config, basestring):
                if view_config not in self.views:
                    logger.warning('Unknown view "{}" given for UI element "{}"!'.format(view_config, self.name))
                else:
                    view = self.views[view_config]
            elif isinstance(view_config, dict):
                raise NotImplementedError
                # This is the part where fine-tuning views will be possible,
                # once passing args&kwargs is implemented, that is
            else:
                logger.error(
                    "Custom view description can only be a string or a dictionary; is {}!".format(type(view_config)))
        elif not view and "default" in config:
            view_config = config["default"]
            if isinstance(view_config, basestring):
                if view_config not in self.views:
                    logger.warning('Unknown view "{}" given for UI element "{}"!'.format(view_config, self.name))
                else:
                    view = self.views[view_config]
            elif isinstance(view_config, dict):
                raise NotImplementedError  # Again, this is for fine-tuning
        elif not view:
            view = self.get_default_view()
        self.view = view(self.o, self.entry_height, self)

    def get_default_view(self):
        """Decides on the view to use for UI element when config file has 
        no information on it."""
        if "b&w-pixel" in self.o.type:
            return self.views["SixteenPtView"]
        elif "char" in self.o.type:
            return self.views["TextView"]
        else:
            raise ValueError("Unsupported display type: {}".format(repr(self.o.type)))

    def before_foreground(self):
        """Hook for child UI elements. Is called each time to_foreground is called."""
        pass

    def before_activate(self):
        """Hook for child UI elements, is called each time activate() is called. 
        Is the perfect place to clear any flags that you don't want to persist 
        between multiple activations of a single instance of an UI element.

        For a start, resets the ``pointer`` to the ``start_pointer``."""
        self.pointer = self.start_pointer

    def to_foreground(self):
        """ Is called when UI element's ``activate()`` method is used, sets flags
            and performs all the actions so that UI element can display its contents
            and receive keypresses. Also, refreshes the screen."""
        logger.info("{0} enabled".format(self.name))
        self.before_foreground()
        self.reset_scrolling()
        self.in_foreground = True
        self.view.refresh()
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
        logger.info("{0} activated".format(self.name))
        self.before_activate()
        self.to_foreground()
        while self.in_foreground:  # All the work is done in input callbacks
            self.idle_loop()
        return_value = self.get_return_value()
        logger.info("{} exited".format(self.name))
        return return_value

    def get_return_value(self):
        """To be overridden by child UI elements. Return value will be returned when
           UI element's ``activate()`` exits."""
        return None  # Default value to indicate that no meaningful result was returned

    def deactivate(self):
        """Sets a flag that signals the UI element's ``activate()`` to return."""
        self.in_foreground = False
        self.o.noCursor()
        logger.info("{} deactivated".format(self.name))

    # Scroll functions - will likely be moved into a mixin or views later on

    @to_be_foreground
    def scroll(self):
        if self.scrolling["enabled"] and not self.scrolling["current_finished"] and self.scrolling["current_scrollable"]:
            self.scrolling["counter"] += 1
            if self.scrolling["counter"] == 10:
                self.scrolling["pointer"] += 1
                self.scrolling["counter"] = 0
                self.view.refresh()

    def reset_scrolling(self):
        self.scrolling["current_finished"] = False
        self.scrolling["pointer"] = 0
        self.scrolling["counter"] = 0

    # Debugging helpers - you can set them as callbacks for keys you don't use

    def print_contents(self):
        """ A debug method. Useful for hooking up to an input event so that
            you can see the representation of current UI element's contents. """
        logger.info(self.contents)

    def print_name(self):
        """ A debug method. Useful for hooking up to an input event so that
            you can see which UI element is currently processing input events. """
        logger.info("Active UI element is {0}".format(self.name))

    # Callbacks for moving up and down in the entry list

    @to_be_foreground
    def move_down(self):
        """ Moves the pointer one entry down, if possible.
        |Is typically used as a callback from input event processing thread.
        |TODO: support going from bottom to top when pressing "down" with
        last entry selected."""
        if self.pointer < (len(self.contents) - 1):
            logger.debug("moved down")
            self.pointer += 1
            self.reset_scrolling()
            self.view.refresh()
            return True
        else:
            return False

    @to_be_foreground
    def page_down(self):
        """ Scrolls up a full screen of entries, if possible.
            If not possible, moves as far as it can."""
        counter = self.view.get_entry_count_per_screen()
        while counter != 0 and self.pointer < (len(self.contents) - 1):
            logger.debug("moved down")
            self.pointer += 1
            counter -= 1
        self.view.refresh()
        self.reset_scrolling()
        return True

    @to_be_foreground
    def move_up(self):
        """ Moves the pointer one entry up, if possible.
        |Is typically used as a callback from input event processing thread.
        |TODO: support going from top to bottom when pressing "up" with
        first entry selected."""
        if self.pointer != 0:
            logger.debug("moved up")
            self.pointer -= 1
            self.view.refresh()
            self.reset_scrolling()
            return True
        else:
            return False

    @to_be_foreground
    def page_up(self):
        """ Scrolls down a full screen of UI entries, if possible.
            If not possible, moves as far as it can."""
        counter = self.view.get_entry_count_per_screen()
        while counter != 0 and self.pointer != 0:
            logger.debug("moved down")
            self.pointer -= 1
            counter -= 1
        self.view.refresh()
        self.reset_scrolling()
        return True

    @to_be_foreground
    def select_entry(self):
        """To be overridden by child UI elements. Is executed when ENTER is pressed
           in UI element."""
        logger.debug(self.contents[self.pointer])

    # Working with the keymap

    @to_be_foreground
    def set_keymap(self):
        """Sets the input device's keycode-to-callback mapping. Re-starts the input device because ofpassing-variables-between-threads issues."""
        self.i.stop_listen()
        self.i.set_keymap(self.keymap)
        self.i.listen()

    def generate_keymap(self):
        """Makes the keymap dictionary for the input device."""
        # Has to be in a function because otherwise it will be a SyntaxError
        self.keymap.update({
            "KEY_UP": lambda: self.move_up(),
            "KEY_DOWN": lambda: self.move_down(),
            "KEY_PAGEUP": lambda: self.page_up(),
            "KEY_PAGEDOWN": lambda: self.page_down(),
            "KEY_ENTER": lambda: self.select_entry()
        })
        if self.exitable:
            self.keymap["KEY_LEFT"] = lambda: self.deactivate()

    def set_contents(self, contents):
        """Sets the UI element contents and triggers pointer recalculation in the view."""
        self.validate_contents(contents)
        # Copy-ing the contents list is necessary because it can be modified
        # by UI elements that are based on this class
        self.contents = copy(contents)
        self.process_contents()
        self.view.fix_pointers_on_contents_update()

    def validate_contents(self, contents):
        """A hook to validate contents before they're set. If validation is unsuccessful,
        raise exceptions (it's better if exception message contains the faulty entry).
        Does not check if the contents are falsey."""
        # if not contents:
        #    raise ValueError("UI element 'contents' argument has to be set to a non-empty list!")
        for entry in contents:
            entry_repr = entry[0]
            if not isinstance(entry_repr, basestring) and not isinstance(entry_repr, list):
                raise Exception("Entries can be either strings or lists of strings - {} is neither!".format(entry))
            if isinstance(entry_repr, list):
                for entry_str in entry_repr:
                    if not isinstance(entry_str, basestring):
                        raise Exception("List entries can only contain strings - {} is not a string!".format(entry_str))

    def process_contents(self):
        """Processes contents for custom callbacks. Currently, only 'exit' calbacks are supported.

        If ``self.append_exit`` is set, it goes through the menu and removes every callback which either is ``self.deactivate`` or is just a string 'exit'.
        |Then, it appends a single "Exit" entry at the end of menu contents. It makes dynamically appending entries to menu easier and makes sure there's only one "Exit" callback, at the bottom of the menu."""
        if self.append_exit:
            # filtering possible duplicate exit entries
            for entry in self.contents:
                if len(entry) > 1 and entry[1] == 'exit':
                    self.contents.remove(entry)
            self.contents.append(self.exit_entry)
        logger.debug("{}: contents processed".format(self.name))


class BaseListBackgroundableUIElement(BaseListUIElement):
    """This is a base UI element for list-like UI elements.
       This UI element has the ability to go into background. It's usually for the cases when
       an UI element can call another UI element, after the second UI element returns,
       context has to return to the first UI element - like in nested menus.

       This UI element has built-in scrolling of entries - if the entry text is longer
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
        logger.debug("{0} disabled".format(self.name))

    def activate(self):
        """ A method which is called when UI element needs to start operating.
            Is blocking, sets up input&output devices, renders the UI element and
            waits until self.in_background is False, while UI element callbacks
            are executed from the input listener thread."""
        logger.info("{0} activated".format(self.name))
        self.before_activate()
        self.to_foreground()
        while self.in_background:  # All the work is done in input callbacks
            self.idle_loop()
        return_value = self.get_return_value()
        logger.info("{} exited".format(self.name))
        return return_value

    def deactivate(self):
        """Sets a flag that signals the UI element's ``activate()`` to return."""
        self.in_background = False
        BaseListUIElement.deactivate(self)


# Views.

class TextView():
    first_displayed_entry = 0
    last_displayed_entry = None

    def __init__(self, o, entry_height, ui_element):
        self.o = o
        self.entry_height = entry_height
        self.el = ui_element

    @property
    def in_foreground(self):
        # Is necessary so that @to_be_foreground works
        # Is to_be_foreground even necessary here?
        return self.el.in_foreground

    def get_entry_count_per_screen(self):
        return self.get_fow_height_in_chars() / self.entry_height

    def get_fow_width_in_chars(self):
        return self.o.cols

    def get_fow_height_in_chars(self):
        return self.o.rows

    def fix_pointers_on_contents_update(self):
        """Boundary-checks ``pointer``, re-sets ``last`` & ``first_displayed_entry`` pointers
           and calculates the value for ``last_displayed_entry`` pointer."""
        self.el.pointer = clamp_list_index(self.el.pointer, self.el.contents)  # Makes sure the pointer isn't >
        full_entries_shown = self.get_entry_count_per_screen()
        entry_count = len(self.el.contents)
        self.first_displayed_entry = 0
        if full_entries_shown > entry_count:  # Display is capable of showing more entries than we have, so the last displayed entry is the last menu entry
            # There are some free display rows, adjusting last_displayed_entry
            self.last_displayed_entry = entry_count - 1
        else:
            # There are no empty spaces on the display
            self.last_displayed_entry = full_entries_shown - 1  # We start numbering entries with 0, so 4-row screen would show entries 0-3
        # print("First displayed entry is {}".format(self.first_displayed_entry))
        # print("Last displayed entry is {}".format(self.last_displayed_entry))

    def fix_pointers_on_refresh(self):
        if self.el.pointer < self.first_displayed_entry:
            logger.debug("Pointer went too far to top, correcting")
            self.last_displayed_entry -= self.first_displayed_entry - self.el.pointer  # The difference will mostly be 1 but I guess it might be more in case of concurrency issues
            self.first_displayed_entry = self.el.pointer
        if self.el.pointer > self.last_displayed_entry:
            logger.debug("Pointer went too far to bottom, correcting")
            self.first_displayed_entry += self.el.pointer - self.last_displayed_entry
            self.last_displayed_entry = self.el.pointer
        logger.debug("First displayed entry is {}".format(self.first_displayed_entry))
        logger.debug("Last displayed entry is {}".format(self.last_displayed_entry))

    def entry_is_active(self, entry_num):
        return entry_num == self.el.pointer

    def get_displayed_text(self):
        """Generates the displayed data for a character-based output device. The output of this function can be fed to the o.display_data function.
        |Corrects last&first_displayed_entry pointers if necessary, then gets the currently displayed entries' numbers, renders each one 
        of them and concatenates them into one big list which it returns.
        |Doesn't support partly-rendering entries yet."""
        displayed_data = []
        disp_entry_positions = range(self.first_displayed_entry, self.last_displayed_entry + 1)
        for entry_num in disp_entry_positions:
            displayed_entry = self.render_displayed_entry(entry_num)
            displayed_data += displayed_entry
        logger.debug("Displayed data: {}".format(displayed_data))
        return displayed_data

    def render_displayed_entry(self, entry_num):
        """Renders an UI element entry by its position number in self.contents, determined also by display width, self.entry_height and entry's representation type.
        If entry representation is a string, splits it into parts as long as the display's width in characters.
           If active flag is set, appends a "*" as the first entry's character. Otherwise, appends " ".
           TODO: omit " " and "*" if entry height matches the display's row count.
        If entry representation is a list, it returns that list as the rendered entry, trimming and padding with empty strings when necessary (to match the ``entry_height``).
        """
        rendered_entry = []
        entry = self.el.contents[entry_num][0]
        active = self.entry_is_active(entry_num)
        display_columns = self.get_fow_width_in_chars()
        avail_display_chars = (display_columns * self.entry_height)
        if type(entry) in [str, unicode]:
            if active:
                # Scrolling only works with strings for now
                # Maybe scrolling should be part of view, too?
                # Likely, yes.
                self.el.scrolling["current_scrollable"] = len(entry) > avail_display_chars
                self.el.scrolling["current_finished"] = len(entry) - self.el.scrolling["pointer"] < avail_display_chars
                if self.el.scrolling["current_scrollable"] and not self.el.scrolling["current_finished"]:
                    entry = entry[self.el.scrolling["pointer"]:]
            rendered_entry.append(entry[:display_columns])  # First part of string displayed
            entry = entry[display_columns:]  # Shifting through the part we just displayed
            for row_num in range(
                    self.entry_height - 1):  # First part of string done, if there are more rows to display, we give them the remains of string
                rendered_entry.append(entry[:display_columns])
                entry = entry[display_columns:]
        elif type(entry) == list:
            entry = entry[
                    :self.entry_height]  # Can't have more arguments in the list argument than maximum entry height
            while len(entry) < self.entry_height:  # Can't have less either, padding with empty strings if necessary
                entry.append('')
            return [str(entry_str)[:display_columns] for entry_str in entry]
        else:
            # How did this slip past the check on set_contents?
            raise Exception("Entries may contain either strings or lists of strings as their representations")
        logger.debug("Rendered entry: {}".format(rendered_entry))
        return rendered_entry

    def get_active_line_num(self):
        return (self.el.pointer - self.first_displayed_entry) * self.entry_height

    @to_be_foreground
    def refresh(self):
        logger.debug("{}: refreshed data on display".format(self.el.name))
        self.fix_pointers_on_refresh()
        displayed_data = self.get_displayed_text()
        self.o.noCursor()
        self.o.display_data(*displayed_data)
        self.o.setCursor(self.get_active_line_num(), 0)
        self.o.cursor()


class EightPtView(TextView):
    charwidth = 6
    charheight = 8
    x_offset = 2
    x_scrollbar_offset = 5
    scrollbar_y_offset = 1

    def get_fow_width_in_chars(self):
        return (self.o.width - self.x_scrollbar_offset) / self.charwidth

    def get_fow_height_in_chars(self):
        return self.o.height / self.charheight

    @to_be_foreground
    def refresh(self):
        logger.debug("{}: refreshed data on display".format(self.el.name))
        self.fix_pointers_on_refresh()
        image = self.get_displayed_image(cursor_y=self.get_active_line_num())
        self.o.display_image(image)

    def get_scrollbar_top_bottom(self):
        scrollbar_max_length = self.o.height - (self.scrollbar_y_offset * 2)
        total_entry_count = len(self.el.contents)
        entries_before = self.first_displayed_entry
        entries_after = total_entry_count - self.last_displayed_entry - 1
        entries_on_screen = total_entry_count - entries_before - entries_after
        if entries_on_screen >= total_entry_count:
            # No scrollbar if there are no entries not shown on the screen
            return 0, 0
        # Scrollbar length per one entry
        length_unit = float(scrollbar_max_length) / total_entry_count
        top = self.scrollbar_y_offset + int(entries_before * length_unit)
        length = int(entries_on_screen * length_unit)
        bottom = top + length
        return top, bottom

    @to_be_foreground
    def get_displayed_image(self, cursor_x=0, cursor_y=None):
        """Generates the displayed data for a canvas-based output device. The output of this function can be fed to the o.display_image function.
        |Doesn't support partly-rendering entries yet."""
        menu_text = self.get_displayed_text()
        c = Canvas(self.o)
        scrollbar_coordinates = self.get_scrollbar_top_bottom()
        # Drawing scrollbar, if applicable
        if scrollbar_coordinates == (0, 0):
            # left offset is dynamic and depends on whether there's a scrollbar or not
            left_offset = self.x_offset
        else:
            left_offset = self.x_scrollbar_offset
            y1, y2 = scrollbar_coordinates
            c.rectangle((1, y1, 2, y2))
        #Drawing the text itself
        for i, line in enumerate(menu_text):
            y = (i * self.charheight - 1) if i != 0 else 0
            c.text(line, (left_offset, y))
        if cursor_y is not None:
            c_x = cursor_x * self.charwidth + 1
            c_y = cursor_y * self.charheight + 1
            cursor_dims = (
                c_x - 1 + left_offset,
                c_y - 1,
                c_x + self.charwidth * len(menu_text[cursor_y]) + left_offset,
                c_y + self.charheight
            )
            c.invert_rect_colors(cursor_dims)
        return c.get_image()


class SixteenPtView(EightPtView):
    charwidth = 8
    charheight = 16

    @to_be_foreground
    def get_displayed_image(self, cursor_x=0, cursor_y=None):
        """Generates the displayed data for a canvas-based output device. The output of this function can be fed to the o.display_image function.
        |Doesn't support partly-rendering entries yet."""
        menu_text = self.get_displayed_text()
        c = Canvas(self.o)
        scrollbar_coordinates = self.get_scrollbar_top_bottom()
        # Drawing scrollbar, if applicable
        if scrollbar_coordinates == (0, 0):
            # left offset is dynamic and depends on whether there's a scrollbar or not
            left_offset = self.x_offset
        else:
            left_offset = self.x_scrollbar_offset
            y1, y2 = scrollbar_coordinates
            c.rectangle((1, y1, 2, y2))
        #Drawing the text itself
        #http://pillow.readthedocs.io/en/3.1.x/reference/ImageFont.html
        font = c.load_font("Fixedsys62.ttf", 16)
        for i, line in enumerate(menu_text):
            y = (i * self.charheight - 1) if i != 0 else 0
            c.text(line, (left_offset, y), font=font)
        # Drawing cursor, if enabled
        if cursor_y is not None:
            c_x = cursor_x * self.charwidth
            c_y = cursor_y * self.charheight
            cursor_dims = (
                c_x - 1 + left_offset,
                c_y - 1,
                c_x + self.charwidth * len(menu_text[cursor_y]) + left_offset,
                c_y + self.charheight
            )
            c.invert_rect_colors(cursor_dims)
        return c.get_image()


class MainMenuTripletView(SixteenPtView):
    # TODO: enable scrolling

    charwidth = 8
    charheight = 16

    def __init__(self, *args, **kwargs):
        SixteenPtView.__init__(self, *args, **kwargs)
        self.charheight = self.o.height / 3

    @to_be_foreground
    def get_displayed_canvas(self, cursor_x=0, cursor_y=None):
        # This view doesn't have a cursor, instead, the entry that's currently active is in the display center
        c = Canvas(self.o)
        central_position = (10, 16)
        font = c.load_font("Fixedsys62.ttf", 32)
        current_entry = self.el.contents[self.el.pointer]
        c.text(current_entry[0], central_position, font=font)
        font = c.load_font("Fixedsys62.ttf", 16)
        if self.el.pointer != 0:
            line = self.el.contents[self.el.pointer - 1][0]
            c.text(line, (2, 0), font=font)
        if self.el.pointer < len(self.el.contents) - 1:
            line = self.el.contents[self.el.pointer + 1][0]
            c.text(line, (2, 48), font=font)
        return c.get_image()
