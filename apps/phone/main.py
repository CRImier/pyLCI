from apps import ZeroApp
from ui import Refresher
from ui.base_ui import BaseUIElement

class InputScreen(BaseUIElement):

    def __init__(self, i, o):
       self.i = i
       self.o = o

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
        self.status_screen = StatusScreen(self.i, self.o)

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
        pass
