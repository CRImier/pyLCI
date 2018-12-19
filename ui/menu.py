from threading import Event
from time import sleep

from base_list_ui import BaseListUIElement, to_be_foreground
from loading_indicators import LoadingBar
from utils import clamp, clamp_list_index

from helpers import setup_logger

logger = setup_logger(__name__, "warning")


class MenuExitException(Exception):
    """An exception that you can throw from a menu callback to exit the menu that
       the callback was called from (and underlying menus, if necessary)"""
    pass


class Menu(BaseListUIElement):
    """Implements a menu which can be used to navigate through your application,
    output a list of values or select actions to perform. Is one of the most used
    UI elements, used both in system core and in most of the applications."""

    pointer = 0  #: number of currently selected menu entry, starting from 0.
    in_background = False  #: flag which indicates whether menu is currently active, either being displayed or just waiting in background (for example, when you go into a sub-menu, the parent menu will still be considered active).
    in_foreground = False  #: flag which indicates whether menu is currently displayed.
    exit_exception = False

    def __init__(self, *args, **kwargs):
        """Initialises the Menu object.

        Args:

            * ``contents``: list of menu entries which was passed either to ``Menu`` constructor or to ``menu.set_contents()``.

              Menu entry is a list, where:
                 * ``entry[0]`` (entry label) is usually a string which will be displayed in the UI, such as "Menu entry 1". If ``entry_height`` > 1, can be a list of strings, each of those strings will be shown on a separate display row.
                 * ``entry[1]`` (entry callback) is a function which is called when the user presses Enter.

                   * Can be omitted if you don't need to have any actions taken upon activation of the entry.
                   * You can supply 'exit' (a string, not a function) if you want a menu entry that exits the menu when the user presses Enter.

                 * ``entry[2]`` (entry second callback) is a callback for the right key press.

              If you want to set contents after the initialisation, please, use set_contents() method.*
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``name``: Menu name which can be used internally and for debugging.
            * ``entry_height``: number of display rows one menu entry occupies.
            * ``append_exit``: Appends an "Exit" alement to menu contents.
            * ``catch_exit``: If ``MenuExitException`` is received and catch_exit is False, it passes ``MenuExitException`` to the parent menu so that it exits, too. If catch_exit is True, MenuExitException is not passed along.
            * ``exitable``: Decides if menu can exit by pressing ``KEY_LEFT``. Set by default and disables ``KEY_LEFT`` callback if unset. Is used for ZPUI main menu, not advised to be used in other settings.
            * ``contents_hook``: A function that is called every time menu goes in foreground that returns new menu contents. Allows to almost-dynamically update menu contents.

        """
        self.catch_exit = kwargs.pop("catch_exit", True)
        self.contents_hook = kwargs.pop("contents_hook", None)
        BaseListUIElement.__init__(self, *args, **kwargs)

    def before_activate(self):
        # Clearing flags before the menu is activated
        self.exit_exception = False

    def before_foreground(self):
        if callable(self.contents_hook):
            self.set_contents(self.contents_hook())

    def get_return_value(self):
        if self.exit_exception:
            if not self.catch_exit:
                logger.info("{} received MenuExitException, raising it further".format(self.name))
                raise MenuExitException

    @to_be_foreground
    def select_entry(self, callback_number=1):
        """ Gets the currently specified entry's description from self.contents and executes the callback, if set.
        |Is typically used as a callback from input event processing thread.
        |After callback's execution is finished, sets the keymap again and refreshes the screen.
        |If MenuExitException is returned from the callback, exits menu."""
        logger.debug("entry selected")
        self.to_background()
        entry = self.contents[self.pointer]
        if len(entry) > callback_number:
            # Current menu entry has a callback
            if entry == self.exit_entry:
                # It's an exit entry, exiting
                self.deactivate()
                return
            try:
                entry[callback_number]()
            except MenuExitException:
                self.exit_exception = True
            finally:
                if self.exit_exception:
                    self.deactivate()
                    return
                else:
                    self.reset_scrolling()
                    self.to_foreground()
        else:
            self.reset_scrolling()
            self.to_foreground()

    def process_right_press(self):
        """Calls the second callback on the right button press."""
        self.select_entry(callback_number=2)


class MenuRenderingMixin(object):
    """A mixin to add Menu-specific rendering to views.
    If you're making your own view for BaseListUIElements and want it to
    work with menu UI elements, you will probably want to use this mixin,
    like this:

    .. code-block:: python

        class MeEightPtView(MenuRenderingMixin, EightPtView):
            pass

    """

    def draw_triangle(self, c, index):
        contents_entry = self.el.contents[self.first_displayed_entry + index/self.el.entry_height]
        if len(contents_entry) > 2 and callable(contents_entry[2]):
            tw, th = self.charwidth / 2, self.charheight / 2
            right_offset = 1
            top_offset = (self.charheight - th) / 2
            coords = (
                (str(-1*(right_offset+tw)), index * self.charheight + top_offset),
                (str(-1*(right_offset+tw)), index * self.charheight + top_offset + th),
                (str(-1*(right_offset)), index * self.charheight + th),
            )
            c.polygon(coords, fill=c.default_color)

    def draw_menu_text(self, c, menu_text, left_offset):
        for i, line in enumerate(menu_text):
            y = (i * self.charheight - 1) if i != 0 else 0
            c.text(line, (left_offset, y), font=self.font)
            if "b&w-pixel" in self.o.type:
                self.draw_triangle(c, i)


Menu.view_mixin = MenuRenderingMixin


class MessagesMenu(Menu):
    """A modified version of the Menu class for displaying a list of messages and loading new ones"""

    load_more_possible = True
    load_more_marker = ["Load more"]

    def __init__(self, *args, **kwargs):
        self.load_more_callback = kwargs.pop("load_more_callback", None)
        self.load_more_trigger_point = kwargs.pop("load_more_trigger_point", 0)
        self.load_more_allow_refresh = Event()
        self.load_more_allow_refresh.set()

        Menu.__init__(self, *args, **kwargs)

    def before_activate(self):
        Menu.before_activate(self)
        self.pointer = clamp(len(self.contents) - 2, 0, len(self.contents)-1)
        if self.contents: # Not empty
		self.add_load_more_marker()

    def add_load_more_marker(self):
	if [self.load_more_marker] not in self.contents:
	        self.contents = [self.load_more_marker] + self.contents

    def remove_load_more_marker(self):
        while self.load_more_marker in self.contents:
            self.contents.remove(self.load_more_marker)

    def load_more(self):
        self.load_more_allow_refresh.clear()
        before = len(self.contents)
	self.remove_load_more_marker()
	has_loaded_more_events = True
	contents_added = False
        counter = 0
        li = None
	while has_loaded_more_events and not contents_added:
                if counter == 5: # the user is let down, let's at least show them stuff is happening
                    li = LoadingBar(self.i, self.o, message="Loading messages", name="{} - load_more() LoadingBar")
                    li.run_in_background()
	        has_loaded_more_events = self.load_more_callback()
                logger.debug("Loaded more events!")
		if has_loaded_more_events:
			self.remove_load_more_marker()
			self.add_load_more_marker()
		        after = len(self.contents)
			difference = after-before
			if difference > 0:
				contents_added = True
				logger.info("Loaded {} messages".format(difference))
			        self.pointer += (after-before)+1
			else:
				logger.info("Loaded events but no messages, retrying")
			self.pointer = clamp_list_index(self.pointer, self.contents)
		else:
			self.remove_load_more_marker()
                counter += 1
        if li: # LoadingBar fired up, need to stop it now
            li.stop()
            sleep(0.5) # until it actually stops =D
            self.activate_input() #reset keymap back to normal
        self.load_more_allow_refresh.set()
        self.refresh()

    def refresh(self):
        if not self.load_more_allow_refresh.isSet():
            return
        Menu.refresh(self)

    @to_be_foreground
    def move_up(self):
        Menu.move_up(self)

        if self.pointer <= self.load_more_trigger_point:
            self.load_more()
