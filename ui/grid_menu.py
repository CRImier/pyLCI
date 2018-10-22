from time import sleep

from base_ui import BaseUIElement
from canvas import Canvas

class GridMenu(BaseUIElement):

	GRID_WIDTH = 3
	GRID_HEIGHT = 3

	def __init__(self, i, o, contents, name="GridMenu"):

		BaseUIElement.__init__(self, i, o, name)

		self.c = Canvas(self.o)

		self.contents = contents
		self.selected_option = {'x': 1, 'y': 1}

	def get_return_value(self):
		pass

	def generate_keymap(self):
		return {
			"KEY_RIGHT": "move_right",
			"KEY_LEFT": "move_left",
			"KEY_UP": "move_up",
			"KEY_DOWN": "move_down",
			"KEY_ENTER": "accept_value",
			"KEY_F1": "exit_menu"
		}

	def idle_loop(self):
		sleep(0.1)

	def exit_menu(self):
		self.deactivate()

	def move_right(self):
		self._move_cursor(1, 0)

	def move_left(self):
		self._move_cursor(-1, 0)

	def move_up(self):
		self._move_cursor(0, -1)

	def move_down(self):
		self._move_cursor(0, 1)

	def accept_value(self):
		pass

	def draw_menu(self):
		self.c.clear()

		step_width = self.c.width / self.GRID_WIDTH
		step_height = self.c.height / self.GRID_HEIGHT

		for x in range(1, self.GRID_WIDTH):
			self.c.line((x*step_width, 0, x*step_width, self.c.height))

			for y in range(1, self.GRID_HEIGHT):
				self.c.line((0, y*step_height, self.c.width, y*step_height))

		selected_x = (self.selected_option['x']-1)*step_width
		selected_y = (self.selected_option['y']-1)*step_height
		self.c.invert_rect((selected_x, selected_y, selected_x+step_width, selected_y+step_height))

		self.c.display()

	def refresh(self):
		self.draw_menu()

	def _move_cursor(self, x_mod, y_mod):
		new_x = self.selected_option['x'] + x_mod
		new_y = self.selected_option['y'] + y_mod

		if new_x >= 1 and new_x <= 3:
			if new_y >= 1 and new_y <= 3:
				self.selected_option['x'] = new_x
				self.selected_option['y'] = new_y

		self.refresh()