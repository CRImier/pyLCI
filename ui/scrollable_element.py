from __future__ import division

from textwrap import wrap
from time import sleep, time

from PIL.ImageDraw import ImageDraw
from luma.core.render import canvas

from helpers import setup_logger
from ui.utils import to_be_foreground, clamp

logger = setup_logger(__name__, "warning")


class Scrollbar(object):
    def __init__(self, o, width=2, min_height=1, margin=1, color="white"):
        self.screen = o
        self._width = width
        self.margin = margin
        self.min_height = min_height
        self.color = color
        self._progress = 0  # 0-1 range, 0 is top, 1 is bottom
        self.height = 0  # 0-1 range, 0 is minimum size, 1 is whole screen

    def draw(self, draw):
        # type: (ImageDraw) -> None
        rect = self.get_coords()
        draw.rectangle(rect, fill=self.color)

    def get_coords(self):
        height_px = self.screen.height * self.height
        height_px = max(height_px, self.min_height)  # so we always have something to show
        y_pos = self.progress * self.screen.height
        rect = (
            self.margin, y_pos,
            self._width, y_pos + height_px
        )
        return rect

    @property
    def width(self):
        # Returns the total width, with margins
        return self.margin * 2 + self._width

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = clamp(value, 0, 1)


class HideableScrollbar(Scrollbar):

    def __init__(self, o, width=2, min_height=1, margin=1, color="white", fade_time=1.5):
        super(HideableScrollbar, self).__init__(o, width, min_height, margin, color)
        self.fade_time = fade_time
        self.last_activity = -fade_time

    def draw(self, draw):
        # type: (ImageDraw) -> None
        rect = self.get_coords()
        color = self.color if time() - self.last_activity < self.fade_time else False
        draw.rectangle(rect, fill=color, outline=color)

    # noinspection PyMethodOverriding
    @Scrollbar.progress.setter
    def progress(self, value):
        self.last_activity = time()
        self._progress = clamp(value, 0, 1)


class TextReader(object):
    """A vertical-scrollable ui element used to read text"""

    # todo : documentation
    def __init__(self, text, i, o, name="TextReader", sleep_interval=1, scroll_speed=2, hide_scrollbar=False,
                 h_scroll=None):
        self.i = i
        self.o = o
        self.name = name
        self.sleep_interval = sleep_interval
        self.scroll_speed = scroll_speed
        self.keymap = dict

        if hide_scrollbar:
            self.scrollbar = HideableScrollbar(self.o, width=2, margin=2)
        else:
            self.scrollbar = Scrollbar(self.o, width=2, margin=2)

        char_width = self.o.charwidth if hasattr(self, "charwidth") else 8  # emulator
        text_width = self.o.cols - (self.scrollbar.width // char_width)

        self._content_width = max([len(line) for line in text.splitlines()])
        self._content_height = len(text)
        self.horizontal_scroll = h_scroll if h_scroll is not None else self._content_width > self.o.cols
        self._content = text.splitlines() if h_scroll else wrap(text, text_width)

        self.in_foreground = False
        self.y_scroll_index = 0
        self.x_scroll_index = 0

    def activate(self):
        logger.info("{0} activated".format(self.name))
        self.to_foreground()
        while self.in_foreground:  # All the work is done in input callbacks
            sleep(self.sleep_interval)
        logger.info("{} exited".format(self.name))
        return None

    @to_be_foreground
    def refresh(self):
        self.scrollbar.height = self.o.rows / len(self._content)
        text = self.get_displayed_text()
        tmp_canvas = canvas(self.o.device)
        image_drawer = tmp_canvas.__enter__()
        self.scrollbar.draw(image_drawer)
        self.draw_text(text, image_drawer, self.scrollbar.width)

        self.o.display_image(tmp_canvas.image)

        del tmp_canvas
        del image_drawer

    def draw_text(self, text, draw, x_offset=2):
        charheight = self.o.charheight if hasattr(self.o, "charheight") else 8
        for line, arg in enumerate(text):
            y = (line * charheight)
            draw.text((x_offset, y), arg, fill='white')

    def get_displayed_text(self):
        start = self.x_scroll_index
        end = start + self.o.rows
        displayed_data = self._content[start:end]
        if self.horizontal_scroll:
            displayed_data = [line[self.y_scroll_index:self.o.cols + self.y_scroll_index] for line in displayed_data]

        return displayed_data

    @to_be_foreground
    def set_keymap(self):
        self.generate_keymap()
        self.i.stop_listen()
        self.i.set_keymap(self.keymap)
        self.i.listen()

    def generate_keymap(self):
        self.keymap = {
            "KEY_UP": lambda: self.move_up(),
            "KEY_DOWN": lambda: self.move_down(),
            "KEY_PAGEUP": lambda: self.page_up(),
            "KEY_PAGEDOWN": lambda: self.page_down(),
            "KEY_LEFT": lambda: self.move_left(),
            "KEY_RIGHT": lambda: self.move_right(),
            "KEY_ENTER": lambda: self.deactivate()
        }

    def to_foreground(self):
        logger.info("{0} enabled".format(self.name))
        self.in_foreground = True
        self.refresh()
        self.set_keymap()

    def deactivate(self):
        self.in_foreground = False

    def move_up(self):
        self.x_scroll_index -= self.scroll_speed
        self.after_move()

    def move_down(self):
        self.x_scroll_index += self.scroll_speed
        self.after_move()

    def move_right(self):
        self.y_scroll_index += self.scroll_speed
        self.after_move()

    def move_left(self):
        self.y_scroll_index -= self.scroll_speed
        self.after_move()

    def page_up(self):
        self.x_scroll_index -= self.scroll_speed * 2
        self.after_move()

    def page_down(self):
        self.x_scroll_index += self.scroll_speed * 2
        self.after_move()

    def after_move(self):
        self.x_scroll_index = clamp(self.x_scroll_index, 0, len(self._content) - self.o.rows + 1)
        self.y_scroll_index = clamp(self.y_scroll_index, 0, self._content_width - self.o.cols + 1)
        self.scrollbar.progress = self.x_scroll_index / len(self._content)
        self.refresh()
