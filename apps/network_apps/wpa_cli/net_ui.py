from ui.menu import MenuRenderingMixin
from ui import Entry

class NetworkMenuRenderingMixin(MenuRenderingMixin):
    net_info_right_offset = 2

    def draw_graphic(self, c, index):
        # c is the canvas
        # index is the number of the entry shown on the screen
        # so, for a 4-entry screen, it's 0, 1, 2 or 3
        entry = self.el.contents[self.first_displayed_entry + index]
        if isinstance(entry, Entry) \
          and hasattr(entry, "network_secured") \
          and hasattr(entry, "network_known"):
            x = c.o.width - c.o.char_width - self.net_info_right_offset
            y = index * self.charheight
            if entry.network_known:
                # draw "k" on the bottom
                c.text("k", (x, y))
            y += c.o.char_height
            if entry.network_secured:
                # draw "s" on the top
                c.text("s", (x, y))
            else:
                # draw "o" on the top
                c.text("o", (x, y))
