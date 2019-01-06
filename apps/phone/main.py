from apps import ZeroApp
from ui import Refresher, NumpadCharInput, Canvas, FunctionOverlay
from ui.base_ui import BaseUIElement
from ui.base_view_ui import BaseView

class InputScreen(NumpadCharInput):

    message = "Input number:"
    default_pixel_view = "InputScreenView"
    def __init__(self, i, o, *args, **kwargs):
        kwargs["message"] = self.message
        NumpadCharInput.__init__(self, i, o, *args, **kwargs)
        self.value = "123456789023456789012345678901234567890"

    def generate_views_dict(self):
        d = NumpadCharInput.generate_views_dict(self)
        d.update({"InputScreenView":InputScreenView})
        return d


class InputScreenView(BaseView):

    top_offset = 8
    value_height = 16
    value_font = ("Fixedsys62.ttf", value_height)

    def __init__(self, o, el):
        BaseView.__init__(self, o, el)
        self.c = Canvas(self.o)

    def gtb(self, text, font):
        return self.c.get_text_bounds(text, font=font)

    def get_onscreen_value_parts(self, value_parts):
        return value_parts[-3:]

    def get_displayed_image(self):
        self.c.clear()
        value = self.el.get_displayed_value()
        value_parts = self.paginate_value(value, self.value_font, width=self.o.width-6)
        onscreen_value_parts = self.get_onscreen_value_parts(value_parts)
        for i, value_part in enumerate(onscreen_value_parts):
            self.c.text(value_part, (3, self.top_offset+self.value_height*i), font=self.value_font)
        return self.c.get_image()

    def paginate_value(self, value, font, width=None):
        width = width if width else self.o.width
        value_parts = []
        while value:
            counter = 0
            while self.gtb(value[:counter], font)[0] <= width and value[counter:]:
                counter += 1
            value_parts.append(value[:counter])
            value = value[counter:]
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
        self.insc_overlay = FunctionOverlay(["deactivate", self.insc_options])
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
