from apps import ZeroApp
from ui import Refresher, NumpadNumberInput, Canvas, FunctionOverlay
from ui.base_ui import BaseUIElement
from ui.base_view_ui import BaseView

from time import sleep

class InputScreen(NumpadNumberInput):

    message = "Input number:"
    default_pixel_view = "InputScreenView"
    def __init__(self, i, o, *args, **kwargs):
        kwargs["message"] = self.message
        kwargs["value"] = "00000000000000000000000000000000000000000000000000000000012345"
        NumpadNumberInput.__init__(self, i, o, *args, **kwargs)

    def generate_views_dict(self):
        d = NumpadNumberInput.generate_views_dict(self)
        d.update({"InputScreenView":InputScreenView})
        return d


class InputScreenView(BaseView):

    top_offset = 8
    value_height = 16
    value_font = ("Fixedsys62.ttf", value_height)

    def __init__(self, o, el):
        BaseView.__init__(self, o, el)
        self.c = Canvas(self.o)
        # storage for text pagination optimisation
        self.width_cache = {}
        self.character_width_cache = {}
        self.build_charwidth_cache()
        print(self.character_width_cache)
        self.prev_value_parts = []

    def build_charwidth_cache(self):
        for char in "".join(self.el.mapping.values()):
            self.character_width_cache[char] = self.gtb(char, font=self.value_font)[0]

    def gtw(self, text, font):
        #print("{} - {}".format(text, [self.character_width_cache[c] for c in text]))
        return sum([self.character_width_cache[c] for c in text])

    def gtb(self, text, font):
        return self.c.get_text_bounds(text, font=font)

    def get_onscreen_value_parts(self, value_parts):
        return value_parts[-3:]

    def get_displayed_image(self):
        self.c.clear()
        value = self.el.get_displayed_value()
        value_parts = self.paginate_value(value, self.value_font, width=self.o.width-6, cache=self.prev_value_parts)
        self.prev_value_parts = value_parts
        onscreen_value_parts = self.get_onscreen_value_parts(value_parts)
        for i, value_part in enumerate(onscreen_value_parts):
            self.c.text(value_part, (3, self.top_offset+self.value_height*i), font=self.value_font)
        return self.c.get_image()

    def paginate_value(self, value, font, width=None, cache=None):
        # This function was optimised because I felt like it was kinda slow...
        # Specifically, because of all the get_text_bounds calls.
        # Now I'm not sure it was worth it - probably was?
        width = width if width else self.o.width
        value_parts = []
        # Let's optimise the counting a little bit and reuse the results of last
        # pagination to speed this one up
        if cache:
            for part in cache[:-1]: #Except the last part since it's incomplete
                if value.startswith(part):
                    value_parts.append(part)
                    value = value[len(part):]
        # Now, onto checking the last part - maybe it's overflown,
        # or maybe it's the first run and we haven't yet calculated the cache
        # (i.e. someone supplied a long value to __init__ of the UI element)
        # Let's go from the end - that will be faster for the most likely usecase.
        while value:
            counter = 0
            while counter < len(value):
                shown_part = value[:-counter] if counter != 0 else value
                remainder = value[-counter:] if counter != 0 else ""
                width_of_next = self.width_cache.get(shown_part, None)
                if width_of_next is None:
                    width_of_next = self.gtw(shown_part, font)
                    self.width_cache[shown_part] = width_of_next
                if width_of_next < width:
                    break
                counter += 1
            value_parts.append(shown_part)
            value = remainder
        print(value_parts)
        return value_parts


class StatusScreen(Refresher):

    def __init__(self, *args, **kwargs):
       Refresher.__init__(self, self.show_status, *args, **kwargs)

    def show_status(self):
       pass


class PhoneApp(ZeroApp):

    menu_name = "Phone"

    def __init__(self, *args, **kwargs):
        ZeroApp.__init__(self, *args, **kwargs)
        self.input_screen = InputScreen(self.i, self.o)
        self.insc_overlay = FunctionOverlay(["deactivate", "backspace"], labels=["Exit", "Backspace"])
        self.insc_overlay.apply_to(self.input_screen)
        #self.status_screen = StatusScreen(self.i, self.o)

    def insc_options(self):
        pass

    def get_context(self, c):
        self.context = c

    def switch_to_input_screen(self, digit=None):
        self.input_screen.activate()

    def on_call(self):
        self.c.request_switch()
        self.show_call_status()

    def get_call_status(self):
        raise NotImplementedError

    def show_call_status(self):
        status = self.get_call_status()
        pass

    def on_start(self):
        self.switch_to_input_screen()
