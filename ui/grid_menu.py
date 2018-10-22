from time import sleep

from base_list_ui import BaseListBackgroundableUIElement
from canvas import Canvas

class GridMenu(BaseListBackgroundableUIElement):

	GRID_WIDTH = 3
	GRID_HEIGHT = 3

	def __init__(self, i, o, contents, name="GridMenu"):

		BaseListBackgroundableUIElement.__init__(self, contents, i, o, name)

		self.c = Canvas(self.o)

		self.selected_option = {'x': 1, 'y': 1}

		self.accepted_value = False

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
		self.accepted_value = True
		self.deactivate()

	def draw_menu(self):
		self.c.clear()

		# Calculate margins
		step_width = self.c.width / self.GRID_WIDTH
		step_height = self.c.height / self.GRID_HEIGHT

		# Draw horizontal and vertical lines
		for x in range(1, self.GRID_WIDTH):
			self.c.line((x*step_width, 0, x*step_width, self.c.height))

			for y in range(1, self.GRID_HEIGHT):
				self.c.line((0, y*step_height, self.c.width, y*step_height))

		# Draw the app names
		for index, item in enumerate(self.contents):
			app_name = self.contents[index][0]
			text_bounds = self.c.get_text_bounds(app_name)

			x_cord = (index%self.GRID_WIDTH)*step_width+(step_width-text_bounds[0])/2
			y_cord = (index//self.GRID_HEIGHT)*step_height+(step_height-text_bounds[1])/2

			self.c.text(app_name, (x_cord, y_cord))

		# Invert the selected cell
		selected_x = (self.selected_option['x']-1)*step_width
		selected_y = (self.selected_option['y']-1)*step_height
		self.c.invert_rect((selected_x, selected_y, selected_x+step_width, selected_y+step_height))

		self.c.display()

	def refresh(self):
		self.draw_menu()

	def _move_cursor(self, x_mod, y_mod):
		new_x = self.selected_option['x'] + x_mod
		new_y = self.selected_option['y'] + y_mod

		if new_x >= 1 and new_x <= self.GRID_WIDTH:
			if new_y >= 1 and new_y <= self.GRID_HEIGHT:
				self.selected_option['x'] = new_x
				self.selected_option['y'] = new_y

		self.refresh()