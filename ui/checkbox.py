import logging

from list_ui_base import BaseListUIElement, TextView, EightPtView, SixteenPtView, to_be_foreground

class Checkbox(BaseListUIElement):
    """Implements a checkbox which can be used to enable or disable some functions in your application. 

    Attributes:

    * ``contents``: list of checkbox elements which was passed either to ``Checkbox`` constructor or to ``checkbox.set_contents()``.

      Checkbox element structure is a list, where:
         * ``element[0]`` (element's representation) is either a string, which simply has the element's value as it'll be displayed, such as "Menu element 1", or, in case of entry_height > 1, can be a list of strings, each of which represents a corresponding display row occupied by the element.
         * ``element[1]`` (element's name) is a name returned by the checkbox upon its exit in a dictionary along with its boolean value.
         * ``element[2]`` (element's state) is the default state assumed by the checkbox. If not present, assumed to be default_state.

      *If you want to set contents after the initalisation, please, use set_contents() method.*
    * ``pointer``: currently selected menu element's number in ``self.contents``.
    * ``in_foreground`` : a flag which indicates if checkbox is currently displayed. If it's not active, inhibits any of menu's actions which can interfere with other menu or UI element being displayed.
    * ``first_displayed_entry`` : Internal flag which points to the number of ``self.contents`` element which is at the topmost position of the checkbox menu as it's currently displayed on the screen
    * ``last_displayed_entry`` : Internal flag which points to the number of ``self.contents`` element which is at the lowest position of the checkbox menu as it's currently displayed on the screen

    """
    states = []
    accepted = False
    exit_entry = ["Accept", None, 'accept']

    def __init__(self, *args, **kwargs):
        """Initialises the Checkbox object.

        Args:

            * ``contents``: a list of element descriptions, which can be constructed as described in the Checkbox object's docstring.
            * ``i``, ``o``: input&output device objects

        Kwargs:

            * ``name``: Checkbox name which can be used internally and for debugging.
            * ``entry_height``: number of display rows one checkbox element occupies.
            * ``default_state``: default state of the element if not supplied.
            * ``final_button_name``: name for the last button that confirms the selection

        """
        self.default_state = kwargs.pop("default_state") if "default_state" in kwargs else False
        self.final_button_name = kwargs.pop("final_button_name") if "final_button_name" in kwargs else "Accept"
        self.exit_entry[0] = self.final_button_name
        BaseListUIElement.__init__(self, *args, **kwargs)

    def set_views_dict(self):
        self.views = {
        "PrettyGraphicalView":ChSixteenPtView, #Left for compatibility
        "SimpleGraphicalView":ChEightPtView, #Left for compatibility
        "SixteenPtView":ChSixteenPtView,
        "EightPtView":ChEightPtView,
        "TextView":ChTextView}

    def get_return_value(self):
        if self.accepted:
            return {self.contents[index][1]:self.states[index] for index, element in enumerate(self.contents) if element != self.exit_entry}
        else:
            return None

    def before_foreground(self):
        #Protecting from a bug that might happen where Checkbox object is reused multiple times
        self.accepted = False

    @to_be_foreground
    def select_entry(self):
        """ Changes the current element's state to the opposite.
        |Is typically used as a callback from input event processing thread. Afterwards, refreshes the screen."""
        logging.debug("element selected")
        if len(self.contents[self.pointer]) > 2 and self.contents[self.pointer][2] == self.exit_entry[2]:
            self.accepted = True
            self.deactivate()
            return
        self.states[self.pointer] = not self.states[self.pointer] #Just inverting.
        self.view.refresh()

    def validate_contents(self, contents):
        assert isinstance(contents, list), "Checkbox contents should be a list"
        for entry in contents:
            assert isinstance(entry[0], basestring), "Checkbox entry first element should be a string - got {} instead".format(repr(entry[0]))
            if len(entry) > 2:
                assert entry[2] in ["accept", True, False], "Checkbox entry third element can only be a boolean or  \"accept\" - got {} instead".format(repr(entry[2]))

    def process_contents(self):
        self.states = [element[2] if len(element)>2 else self.default_state for element in self.contents]
        self.contents.append(self.exit_entry)
        self.states.append(False) #For the final button, to maintain "len(states) == len(self.contents)"
        logging.debug("{}: menu contents processed".format(self.name))


class CheckboxRenderingMixin():

    def entry_is_checked(self, entry_num):
        return self.el.states[entry_num]

    def render_displayed_entry(self, entry_num):
        rendered_entry = []
        entry = self.el.contents[entry_num][0]
        active = self.entry_is_active(entry_num)
        checked = self.entry_is_checked(entry_num)
        display_columns = self.get_fow_width_in_chars()
        avail_display_chars = (display_columns*self.entry_height)-1 #1 char for "*"/" "
        if type(entry) in [str, unicode]:
            if active:
                self.el.scrolling["current_scrollable"] = len(entry) > avail_display_chars
                self.el.scrolling["current_finished"] = len(entry)-self.el.scrolling["pointer"] < avail_display_chars
                if self.el.scrolling["current_scrollable"] and not self.el.scrolling["current_finished"]:
                    entry = entry[self.el.scrolling["pointer"]:]
            if checked:
                rendered_entry.append("*"+entry[:display_columns-1]) #First part of string displayed
            else:
                rendered_entry.append(" "+entry[:display_columns-1])
            entry_content = entry[display_columns-1:]
            for row_num in range(self.entry_height-1): #First part of string done, if there are more rows to display, we give them the remains of string
                rendered_entry.append(entry[:display_columns])
                entry = entry[display_columns:]
        elif type(entry) == list:
            entry = entry[:self.entry_height] #Can't have more arguments in the list argument than maximum entry height
            if checked:
                entry[0][0] == "*"
            else:
                entry[0][0] == " "
            while len(entry) < self.entry_height: #Can't have less either, padding with empty strings if necessary
                entry.append('')
            return entry
        else:
            raise Exception("Entries may contain either strings or lists of strings as their representations")
        logging.debug("Rendered entry: {}".format(rendered_entry))
        return rendered_entry

class ChEightPtView(CheckboxRenderingMixin, EightPtView):
    pass

class ChTextView(CheckboxRenderingMixin, TextView):
    pass

class ChSixteenPtView(CheckboxRenderingMixin, SixteenPtView):
    pass
