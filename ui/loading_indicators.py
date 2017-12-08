from ui import Refresher
from ui.utils import clamp
from threading import Thread


class LoadingIndicator(Refresher):

    def __init__(self, i, o, *args, **kwargs):
        Refresher.__init__(self, self.on_refresh, i, o, *args, **kwargs)
        self.t = None

    def on_refresh(self):
        raise NotImplementedError

    def run_in_background(self):
        if self.t is not None or self.in_foreground:
            raise Exception("LoadingIndicator already running!")
        self.t = Thread(target=self.activate)
        self.t.daemon=True
        self.t.start()


class DottedProgressIndicator(LoadingIndicator):

    def __init__(self, i, o, *args, **kwargs):
        LoadingIndicator.__init__(self, i, o, *args, **kwargs)
        self.message = kwargs.pop("message") if "message" in kwargs else "Loading".center(o.cols).rstrip()
        self.dot_count = 0

    def on_refresh(self):
        self.dot_count = (self.dot_count + 1) % 4
        return self.message + '.' * self.dot_count


class ProgressBar(LoadingIndicator):

    def __init__(self, i, o, *args, **kwargs):
        #We need to pop() these arguments instead of using kwargs.get() because they 
        #have to be removed from kwargs to prevent TypeErrors
        self.message = kwargs.pop("message") if "message" in kwargs else "Loading"
        self.fill_char = kwargs.pop("fill_char") if "fill_char" in kwargs else "="
        self.empty_char = kwargs.pop("empty_char") if "empty_char" in kwargs else " "
        self.border_chars = kwargs.pop("border_chars") if "border_chars" in kwargs else "[]"
        self.show_percentage = kwargs.pop("show_percentage") if "show_percentage" in kwargs else False
        self.percentage_offset = kwargs.pop("percentage_offset") if "percentage_offset" in kwargs else 4
        LoadingIndicator.__init__(self, i, o, *args, **kwargs)
        self._progress = 0 # 0-1 range

    @property
    def progress(self):
        return float(self._progress)

    @progress.setter
    def progress(self, value):
        self._progress = clamp(value, 0, 1)
        self.refresh()

    def get_progress_percentage_string(self):
        return '{}%'.format(int(self.progress * 100))

    def get_bar_str(self, size):
        size -= len(self.border_chars)  # to let room for the border chars and/or percentage string
        bar_end = self.border_chars[1]
        if self.show_percentage:
            percentage = self.get_progress_percentage_string()
            #Leaving room for the border chars and/or percentage string
            size -= self.percentage_offset if self.percentage_offset > 0 else len(percentage)
            bar_end += percentage.rjust(self.percentage_offset)

        filled_col_count = int(size * self.progress)
        unfilled_col_count = size - filled_col_count
        fill_str = self.fill_char * int(filled_col_count) + self.empty_char * int(unfilled_col_count)

        bar = '{s}{bar}{e}'.format(
            bar=fill_str,
            s=self.border_chars[0],
            e=bar_end
        )
        return bar

    def on_refresh(self):
        bar = self.get_bar_str(self.o.cols)
        return [self.message.center(self.o.cols), bar]
