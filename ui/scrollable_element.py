from __future__ import division

from textwrap import wrap
from time import sleep, time

from PIL.ImageDraw import ImageDraw
from luma.core.render import canvas

from helpers import setup_logger
from ui.utils import to_be_foreground, clamp

logger = setup_logger(__name__, "warning")


class VerticalScrollbar(object):
    def __init__(self, o, width=1, min_size=1, margin=1, color="white"):
        self.screen = o
        self._width = width
        self.margin = margin
        self.min_size = min_size
        self.color = color
        self._progress = 0  # 0-1 range, 0 is top, 1 is bottom
        self.size = 0  # 0-1 range, 0 is minimum size, 1 is whole screen

    def draw(self, draw):
        # type: (ImageDraw) -> None
        rect = self.get_coords()
        draw.rectangle(rect, fill=self.color)

    def get_coords(self):
        height_px = self.screen.height * self.size
        height_px = max(height_px, self.min_size)  # so we always have something to show
        y_pos = self.progress * self.screen.height
        rect = (
            self.margin, y_pos,
            self.margin + self._width, y_pos + height_px
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


class HorizontalScrollbar(VerticalScrollbar):

    def get_coords(self):
        width_px = self.screen.width * self.size
        width_px = max(width_px, self.min_size)
        x_pos = self.progress * self.screen.width
        rect = (
            x_pos, self.screen.height - self._width - self.margin,
            x_pos + width_px, self.screen.height - self.margin
        )
        return rect

    def draw(self, draw):
        rect = self.get_coords()
        draw.rectangle(
            self.get_background_coords(),
            fill="black",
            outline="black",
        )
        draw.rectangle(rect, fill=self.color)

    def get_background_coords(self):
        return 0, self.screen.height - self.width, self.screen.width, self.screen.height


class HideableVerticalScrollbar(VerticalScrollbar):

    def __init__(self, o, width=1, min_size=1, margin=1, color="white", fade_time=1):
        super(HideableVerticalScrollbar, self).__init__(o, width, min_size, margin, color)
        self.fade_time = fade_time
        self.last_activity = -fade_time

    def draw(self, draw):
        # type: (ImageDraw) -> None
        rect = self.get_coords()
        self.update_color()
        draw.rectangle(rect, fill=self.color, outline=self.color)

    def update_color(self):
        self.color = "white" if time() - self.last_activity < self.fade_time else False

    # noinspection PyMethodOverriding
    @VerticalScrollbar.progress.setter
    def progress(self, value):
        if value == self.progress:
            return
        self.last_activity = time()
        self._progress = clamp(value, 0, 1)


class HideableHorizontalScrollbar(HorizontalScrollbar, HideableVerticalScrollbar):

    def __init__(self, o, width=1, min_size=1, margin=1, color="white", fade_time=1):
        HorizontalScrollbar.__init__(self, o, width, min_size, margin, color)
        HideableVerticalScrollbar.__init__(self, o, width, min_size, margin, color, fade_time)

    def get_coords(self):
        return HorizontalScrollbar.get_coords(self)

    def draw(self, draw):
        self.update_color()
        return HorizontalScrollbar.draw(self, draw)

    # noinspection PyMethodOverriding
    @VerticalScrollbar.progress.setter
    def progress(self, value):
        if value == self.progress:
            return
        self.last_activity = time()
        self._progress = clamp(value, 0, 1)


class TextReader(object):
    """A vertical-scrollable ui element used to read text"""

    # todo : documentation
    def __init__(self, text, i, o, name="TextReader", sleep_interval=1, scroll_speed=2, autohide_scrollbars=True,
                 h_scroll=None):
        self.i = i
        self.o = o
        self.name = name
        self.sleep_interval = sleep_interval
        self.scroll_speed = scroll_speed
        self.keymap = dict

        if autohide_scrollbars:
            self.v_scrollbar = HideableVerticalScrollbar(self.o, margin=2)
            self.h_scrollbar = HideableHorizontalScrollbar(self.o, margin=2)
        else:
            self.v_scrollbar = VerticalScrollbar(self.o)
            self.h_scrollbar = HorizontalScrollbar(self.o)

        char_width = self.o.charwidth if hasattr(self, "charwidth") else 8  # emulator
        text_width = self.o.cols - (self.v_scrollbar.width // char_width)

        self._content_width = max([len(line) for line in text.splitlines()])
        self._content_height = len(text.splitlines())
        self.horizontal_scroll = h_scroll if h_scroll is not None else self._content_width > self.o.cols
        self._content = text.splitlines() if self.horizontal_scroll else wrap(text, text_width)

        self.in_foreground = False
        self.v_scroll_index = 0
        self.h_scroll_index = 0

        self.after_move()

    def activate(self):
        logger.info("{0} activated".format(self.name))
        self.to_foreground()
        while self.in_foreground:  # All the work is done in input callbacks
            sleep(self.sleep_interval)
            self.refresh()  # needed to update the hideable scrollbars
        logger.info("{} exited".format(self.name))
        return None

    @to_be_foreground
    def refresh(self):
        text = self.get_displayed_text()
        tmp_canvas = canvas(self.o.device)
        image_drawer = tmp_canvas.__enter__()
        self.draw_text(text, image_drawer, self.v_scrollbar.width)
        self.v_scrollbar.draw(image_drawer)
        self.h_scrollbar.draw(image_drawer)

        self.o.display_image(tmp_canvas.image)

        del tmp_canvas
        del image_drawer

    def draw_text(self, text, draw, x_offset):
        charheight = self.o.charheight if hasattr(self.o, "charheight") else 8
        for line, arg in enumerate(text):
            y = (line * charheight)
            draw.text((x_offset, y), arg, fill='white')

    def get_displayed_text(self):
        start = self.h_scroll_index
        end = start + self.o.rows
        displayed_data = self._content[start:end]
        if self.horizontal_scroll:
            displayed_data = [line[self.v_scroll_index:self.o.cols + self.v_scroll_index] for line in displayed_data]

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
        self.h_scroll_index -= self.scroll_speed
        self.after_move()

    def move_down(self):
        self.h_scroll_index += self.scroll_speed
        self.after_move()

    def move_right(self):
        self.v_scroll_index += self.scroll_speed
        self.after_move()

    def move_left(self):
        self.v_scroll_index -= self.scroll_speed
        self.after_move()

    def page_up(self):
        self.h_scroll_index -= self.scroll_speed * 2
        self.after_move()

    def page_down(self):
        self.h_scroll_index += self.scroll_speed * 2
        self.after_move()

    def after_move(self):
        self.v_scrollbar.size = self.o.rows / self._content_height
        self.h_scrollbar.size = self.o.cols / self._content_width
        self.h_scroll_index = clamp(self.h_scroll_index, 0, self._content_height - self.o.rows + 1)
        self.v_scroll_index = clamp(self.v_scroll_index, 0, self._content_width - self.o.cols + 1)
        self.v_scrollbar.progress = self.h_scroll_index / self._content_height
        self.h_scrollbar.progress = self.v_scroll_index / self._content_width
        self.refresh()
