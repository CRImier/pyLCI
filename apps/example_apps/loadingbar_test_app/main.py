from time import sleep
from apps.zero_app import ZeroApp
from ui import ProgressTextBar, ProgressCircular, IdleDottedMessage, IdleCircular, Listbox


class LoadingBarExampleApp(ZeroApp):
    def __init__(self, i, o):
        super(LoadingBarExampleApp, self).__init__(i, o)
        self.menu_name = "Loading bar test app"

        self.text_progress = ProgressTextBar(self.i, self.o, refresh_interval=.1, show_percentage=True,
                                             percentage_offset=0)
        self.circular_progress = ProgressCircular(self.i, self.o, show_percentage=True)
        self.dotted_progress_bar = IdleDottedMessage(self.i, self.o, refresh_interval=.1)
        self.throbber = IdleCircular(self.i, self.o, refresh_interval=.1)
        lb_contents = [
            ["Text progress bar", self.text_progress],
            ["Dotted idle ", self.dotted_progress_bar],
            ["Circular progress ", self.circular_progress],
            ["Idle Throbber", self.throbber],
        ]
        self.bar_choice_listbox = Listbox(lb_contents, self.i, self.o)

    def on_start(self):
        super(LoadingBarExampleApp, self).on_start()
        chosen_loading_bar = self.bar_choice_listbox.activate()
        chosen_loading_bar.run_in_background()
        if hasattr(chosen_loading_bar, "progress"):
            for i in range(101):
                chosen_loading_bar.progress = float(i) / 100
                sleep(0.01)
            sleep(1)
            for i in range(101)[::-1]:
                chosen_loading_bar.progress = float(i) / 100
                sleep(0.01)
        else:
            sleep(3)
            chosen_loading_bar.deactivate()
