from apps import ZeroApp
from ui import GridMenu

class MainMenu(ZeroApp):

	menu_name = "Main Menu"

	def on_start(self):
		self.gm = GridMenu(self.i, self.o, contents=[[], [], []])
		self.gm.activate()