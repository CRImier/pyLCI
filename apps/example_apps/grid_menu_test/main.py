from apps import ZeroApp
from ui import GridMenu

def test_func(x):
	print(x)

class MainMenu(ZeroApp):

	menu_name = "Main Menu"

	def on_start(self):
		grid_contents = [
			["111thisistoolong", lambda x=111: test_func(x)], ["222", lambda x=222: test_func(x)], ["333", lambda x=333: test_func(x)],
			["444", lambda x=444: test_func(x)], ["555", lambda x=555: test_func(x)], ["666", lambda x=666: test_func(x)],
			["777", lambda x=777: test_func(x)], ["888", lambda x=888: test_func(x)], ["999", lambda x=999: test_func(x)],
			["211", lambda x=211: test_func(x)]
		]

		self.gm = GridMenu(grid_contents, self.i, self.o)
		self.gm.activate()
