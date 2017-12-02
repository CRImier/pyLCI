# coding=utf-8

from apps.zero_app import ZeroApp
from ui import NumberedMenu


class NumberedInputTestApp(ZeroApp):

    def __init__(self, i, o):
        super(NumberedInputTestApp, self).__init__(i, o)
        self.n_menu = None
        self.menu_name = "Numbered Input Menu"
        self.main_menu_contents = [
            ["hello", self.print_hello],
            ["hello again", self.print_hello],
            ["same", self.print_hello],
            ["ditto", self.print_hello],
            ["hello", self.print_hello],
            ["hello again", self.print_hello],
            ["same", self.print_hello],
            ["ditto", self.print_hello],
            ["hello", self.print_hello],
            ["hello again", self.print_hello],
            ["same", self.print_hello],
            ["ditto", self.print_hello],
            ["ditto", self.print_hello],
            ["ditto", self.print_hello],
            ["ditto", self.print_hello],
            ["ditto", self.print_hello],
            ["nothing new here", self.print_hello]
        ]

    @staticmethod
    def print_hello():
        print("hello")

    def on_start(self):
        super(NumberedInputTestApp, self).on_start()
        self.n_menu = NumberedMenu(
            self.main_menu_contents,
            self.i,
            self.o,
            self.menu_name,
            prepend_numbers=True,
            input_delay=1)
        self.n_menu.activate()
