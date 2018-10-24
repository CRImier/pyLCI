from apps import ZeroApp
from ui import GridMenu

def test_func():
	print("Hello world")

class MainMenu(ZeroApp):

	menu_name = "Grid menu test"

	def on_start(self):
		grid_contents = [
			["111", test_func], ["222", test_func], ["333", test_func],
			["444", test_func], ["555", test_func], ["666", test_func],
			["777", test_func], ["888", test_func], ["999", test_func]
		]

		self.gm = GridMenu(self.i, self.o, contents=grid_contents)
		self.gm.activate()
