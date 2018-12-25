import os

from apps import ZeroApp
from ui import GridMenu, Entry, GridMenuLabelOverlay

from PIL import Image

def test_func(x):
	print(x)

class MainMenu(ZeroApp):

	menu_name = "Main Menu"

	def on_start(self):
		dir = "resources/"
                icons = [f for f in os.listdir(dir) if f.endswith(".png")]
                icon_paths = [[f, os.path.join(dir, f)] for f in icons]
		grid_contents = [Entry(f.rsplit('.', 1)[0].capitalize(), icon=Image.open(p), cb=lambda x=f: test_func(x)) \
                                   for f,p in icon_paths]

		self.gm = GridMenu(grid_contents, self.i, self.o, entry_width=32, draw_lines=False)
                self.overlay = GridMenuLabelOverlay()
                self.overlay.apply_to(self.gm)
		self.gm.activate()
