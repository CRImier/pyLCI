from __future__ import division

import logging
from textwrap import wrap
from time import sleep

from PIL.ImageDraw import ImageDraw
from luma.core.render import canvas

from ui.utils import to_be_foreground, clamp

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Scrollbar(object):
    def __init__(self, o, width=2, min_height=1, margin=1, color="white"):
        self.screen = o
        self._width = width
        self.margin = margin
        self.min_height = min_height
        self.color = color
        self._progress = 0  # 0-1 range, 0 is top, 1 is bottom
        self.height = 0  # 0-1 range, 0 is minimum size, 1 is whole screen
        # todo margin, color

    def draw(self, draw):
        # type: (ImageDraw) -> None
        height_px = self.screen.height * self.height
        height_px = max(height_px, self.min_height)  # so we always have something to show

        y_pos = self.progress * self.screen.height
        rect = (
            self.margin, y_pos,
            self._width, y_pos + height_px
        )
        draw.rectangle(rect, fill=self.color)

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
    pass  # todo: fades out when not moved in while


class ScrollableThingy(object):
    def __init__(self, text_content, i, o, name, sleep_interval=1, scroll_speed=10):
        self.i = i
        self.o = o
        self.name = name
        self.sleep_interval = sleep_interval
        self.scroll_speed = scroll_speed
        self.keymap = dict
        self.scrollbar = Scrollbar(self.o, width=2, margin=2)  # todo: maybe expose those parameters in constructor ?
        text_width = self.o.cols - (self.scrollbar.width // self.o.char_width)
        self.content = wrap(text_content, text_width)
        self.in_foreground = False
        self.scroll_index = 0

    def activate(self):
        logger.info("{0} activated".format(self.name))
        self.to_foreground()
        while self.in_foreground:  # All the work is done in input callbacks
            self.refresh()
            sleep(self.sleep_interval)
        logger.info("{} exited".format(self.name))
        return None

    @to_be_foreground
    def refresh(self):
        self.scrollbar.progress = self.scroll_index / len(self.content)
        self.scrollbar.height = self.o.rows / len(self.content)
        text = self.get_displayed_text()
        tmp_canvas = canvas(self.o.device)
        image_drawer = tmp_canvas.__enter__()
        self.scrollbar.draw(image_drawer)
        self.draw_text(text, image_drawer, self.scrollbar.width)

        self.o.display_image(tmp_canvas.image)

        del tmp_canvas  # todo: ask -> shouldn't I keep it instead ?
        del image_drawer

    def draw_text(self, text, draw, x_offset=2):
        for line, arg in enumerate(text):
            y = (line * self.o.char_height)
            draw.text((x_offset, y), arg, fill='white')

    def get_displayed_text(self):
        start = self.scroll_index
        end = start + self.o.rows
        displayed_data = self.content[start:end]
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
            "KEY_LEFT": lambda: self.deactivate()
        }

    def to_foreground(self):
        logger.info("{0} enabled".format(self.name))
        self.in_foreground = True
        self.set_keymap()

    def deactivate(self):
        self.in_foreground = False

    def move_up(self):
        self.scroll_index -= 1
        self.clamp_scroll()

    def move_down(self):
        self.scroll_index += 1
        self.clamp_scroll()

    def page_up(self):
        self.scroll_index -= self.scroll_speed

    def page_down(self):
        self.scroll_index += self.scroll_speed

    def clamp_scroll(self):
        self.scroll_index = clamp(self.scroll_index, 0, len(self.content) - self.o.rows + 1)
