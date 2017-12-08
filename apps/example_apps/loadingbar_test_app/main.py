from apps.zero_app import ZeroApp
from ui.loading_indicators import ProgressBar


class LoadingBarExampleApp(ZeroApp):
    def __init__(self, i, o):
        super(LoadingBarExampleApp, self).__init__(i, o)
        self.menu_name = "Loading test APP"

        self.loading_screen = ProgressBar(self.i, self.o, refresh_interval=.1, show_percentage=True)
        # todo: uncomment line below to test another indicator
        # self.loading_screen = DottedProgressIndicator(self.i, self.o, refresh_interval=.1, show_percentage=True)

        self.loading_screen.keymap['KEY_RIGHT'] = self.increase_progress

    def increase_progress(self):
        self.loading_screen.progress += .05

    def on_start(self):
        super(LoadingBarExampleApp, self).on_start()
        self.loading_screen.activate()
