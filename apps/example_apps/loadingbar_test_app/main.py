from time import sleep
from apps.zero_app import ZeroApp
from ui import Menu
from ui.loading_indicators import TextProgressBar, IdleThrobber, CircularProgressIndicator

from ui import ProgressBar, DottedProgressIndicator, Listbox

class LoadingBarExampleApp(ZeroApp):
    def __init__(self, i, o):
        super(LoadingBarExampleApp, self).__init__(i, o)
        self.menu_name = "Loading bar test app"

        self.loading_screen = CircularProgressIndicator(self.i, self.o, refresh_interval=.1, show_percentage=True, keymap={"KEY_RIGHT":self.increase_progress})
        # self.loading_screen = IdleThrobber(self.i, self.o, refresh_interval=.1, show_percentage=True)
        # todo: uncomment line below to test another indicator
        # self.loading_screen = DottedProgressIndicator(self.i, self.o, refresh_interval=.1, show_percentage=True)
        self.loading_screen.keymap['KEY_RIGHT'] = self.increase_progress
        lb_contents = [["Progress bar", self.progress_bar],
                       ["Dotted bar", self.dotted_progress_bar]]
        self.bar_choice_listbox = Listbox(lb_contents, self.i, self.o)
        self.progress_bar = ProgressBar(self.i, self.o,
                                          refresh_interval=.1,
                                          show_percentage=True,
                                          percentage_offset=0,
                                          keymap={"KEY_RIGHT":self.increase_progress})

        self.dotted_progress_bar = DottedProgressIndicator(self.i, self.o,
                                                       refresh_interval=.1)

        lb_contents = [["Progress bar", self.progress_bar],
                       ["Dotted bar", self.dotted_progress_bar]]
        self.bar_choice_listbox = Listbox(lb_contents, self.i, self.o)

    def increase_progress(self):
        self.loading_screen.progress += .05

    def on_start(self):
        super(LoadingBarExampleApp, self).on_start()
        chosen_loading_bar = self.bar_choice_listbox.activate()
        chosen_loading_bar.run_in_background()
        if isinstance(chosen_loading_bar, ProgressBar):
            for i in range(101):
                chosen_loading_bar.progress = float(i)/100
                sleep(0.1)
            sleep(2)
            for i in range(101)[::-1]:
                chosen_loading_bar.progress = float(i)/100
                sleep(0.1)
        else:
            sleep(3)
            chosen_loading_bar.deactivate()

