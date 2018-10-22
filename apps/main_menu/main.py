from apps import ZeroApp
from ui import GridMenu

class MainMenu(ZeroApp):

	menu_name = "Main Menu"

	def on_start(self):
		grid_contents = [
			[["111", lambda: print("111")], "222", "333"],
			["444", "555", "666"],
			["777", "888", "999"]
		]

		grid_contents[0][0][1]()

		self.gm = GridMenu(self.i, self.o, contents=grid_contents)
		self.gm.activate()