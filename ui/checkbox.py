import logging

from list_ui_base import BaseListUIElement, to_be_foreground

class Checkbox(BaseListUIElement):
    """Implements a checkbox which can be used to enable or disable some functions in your application. 

    Attributes:

    * ``contents``: list of checkbox elements which was passed either to ``Checkbox`` constructor or to ``checkbox.set_contents()``.

      Checkbox element structure is a list, where:
         * ``element[0]`` (element's representation) is either a string, which simply has the element's value as it'll be displayed, such as "Menu element 1", or, in case of entry_height > 1, can be a list of strings, each of which represents a corresponding display row occupied by the element.
         * ``element[1]`` (element's name) is a name returned by the checkbox upon its exit in a dictionary along with its boolean value.
         * ``element[2]`` (element's state) is the default state assumed by the checkbox. If not present, assumed to be default_state.

      *If you want to set contents after the initalisation, please, use set_contents() method.*
    * ``_contents``: "Working copy" of checkbox contents, basically, a ``contents`` attribute which has been processed by ``self.process_contents``. 
    * ``pointer``: currently selected menu element's number in ``self._contents``.
    * ``in_foreground`` : a flag which indicates if checkbox is currently displayed. If it's not active, inhibits any of menu's actions which can interfere with other menu or UI element being displayed.
    * ``first_displayed_entry`` : Internal flag which points to the number of ``self._contents`` element which is at the topmost position of the checkbox menu as it's currently displayed on the screen
    * ``last_displayed_entry`` : Internal flag which points to the number of ``self._contents`` element which is at the lowest position of the checkbox menu as it's currently displayed on the screen

    """
    states = []
    accepted = True
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
        default_state = **kwargs.pop("default_state") if "default_state" in kwargs else False
        final_button_name = **kwargs.pop("final_button_name") if "final_button_name" in kwargs else "Accept"
        BaseListUIElement.__init__(self, *args, **kwargs)
        self.exit_entry[0] = final_button_name

    def get_return_value(self):
        if self.accepted:
            return {self._contents[index][1]:self.states[index] for index, element in enumerate(self._contents)}
        else:
            return None

    @to_be_foreground
    def select_entry(self):
        """ Changes the current element's state to the opposite.
        |Is typically used as a callback from input event processing thread. Afterwards, refreshes the screen."""
        logging.debug("element selected")
        if self._contents[self.pointer][2] == 'accept':
            self.accepted = True
            self.deactivate()
            return
        self.states[self.pointer] = not self.states[self.pointer] #Just inverting.
        self.refresh()

    def validate_contents(self, contents):
        pass

    def process_contents(self, contents):
        self.states = [element[2] if len(element)>1 else self.default_state for element in contents]
        self.contents.append(self.exit_entry)
        self.states.append(False) #For the final button, to maintain "len(states) == len(self._contents)"
        logging.debug("{}: menu contents processed".format(self.name))

    def get_displayed_data(self):
        """Generates the displayed data in a way that the output device accepts.
           The output of this function can be fed to the o.display_data function."""
        displayed_data = []
        disp_entry_positions = range(self.first_displayed_entry, self.last_displayed_entry+1)
        #print("Displayed entries: {}".format(disp_entry_positions))
        for entry_num in disp_entry_positions:
            displayed_entry = self.render_displayed_entry(entry_num, checked = self.states[entry_num])
            displayed_data += displayed_entry
        #print("Displayed data: {}".format(displayed_data))
        return displayed_data

    def render_displayed_entry(self, entry_num, checked=False):
        """Renders a checkbox element by its position number in self._contents, determined also by display width, self.entry_height and element's representation type.
        If element's representation is a string, splits it into parts as long as the display's width in characters.
           If active flag is set, appends a "*" as the first entry's character. Otherwise, appends " ".
           TODO: omit " " and "*" if element height matches the display's row count.
        If element's representation is a list, it returns that list as the rendered entry, trimming its elements down or padding the list with empty strings to match the element's height as defined.
        """
        rendered_entry = []
        entry_content = self._contents[entry_num][0]
        display_columns = self.o.cols
        if type(entry_content) in [str, unicode]:
            if checked:
                rendered_entry.append("*"+entry_content[:display_columns-1]) #First part of string displayed
                entry_content = entry_content[display_columns-1:] #Shifting through the part we just displayed
            else:
                rendered_entry.append(" "+entry_content[:display_columns-1])
                entry_content = entry_content[display_columns-1:]
            for row_num in range(self.entry_height-1): #First part of string done, if there are more rows to display, we give them the remains of string
                rendered_entry.append(entry_content[:display_columns])
                entry_content = entry_content[display_columns:]
        elif type(entry_content) == list:
            entry_content = entry_content[:self.entry_height] #Can't have more arguments in the list argument than maximum entry height
            if checked:
                entry_content[0][0] == "*"
            else:
                entry_content[0][0] == " "
            while len(entry_content) < self.entry_height: #Can't have less either, padding with empty strings if necessary
                entry_content.append('')
            return entry_content
        else:
            raise Exception("Entries may contain either strings or lists of strings as their representations")
        #print("Rendered entry: {}".format(rendered_entry))
        return rendered_entry
