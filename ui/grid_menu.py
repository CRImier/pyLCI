from time import sleep

from menu import Menu
from canvas import Canvas

class GridMenu(Menu):

	GRID_WIDTH = 3
	GRID_HEIGHT = 3

	def __init__(self, i, o, contents, name="GridMenu"):

		Menu.__init__(self, contents, i, o, name, override_left=False)

		self.view = GridView(o, self, self.GRID_WIDTH, self.GRID_HEIGHT)

	def generate_keymap(self):
		return {
			"KEY_RIGHT": "move_right",
			"KEY_LEFT": "move_left",
			"KEY_UP": "move_up",
			"KEY_DOWN": "move_down",
			"KEY_ENTER": "select_entry",
			"KEY_F1": "exit_menu"
		}

	def idle_loop(self):
		sleep(0.1)

	def exit_menu(self):
		self.deactivate()

	def move_right(self):
		self._move_cursor(1)

	def move_left(self):
		self._move_cursor(-1)

	def move_up(self):
		self._move_cursor(-self.GRID_WIDTH)

	def move_down(self):
		self._move_cursor(self.GRID_WIDTH)

	def refresh(self):
		self.view.refresh()

	def _move_cursor(self, m):
		self.pointer += m
		self.pointer = self.pointer%(self.GRID_WIDTH*self.GRID_HEIGHT)
		self.refresh()


class GridView():

	def __init__(self, o, ui_element, width, height):
		self.c = Canvas(o)
		self.el = ui_element

		self.GRID_WIDTH = width
		self.GRID_HEIGHT = height

	def draw_grid(self):
		self.c.clear()

		# Calculate margins
		step_width = self.c.width / self.GRID_WIDTH
		step_height = self.c.height / self.GRID_HEIGHT

		# Calculate grid index
		item_x = self.el.pointer%self.GRID_WIDTH
		item_y = self.el.pointer//self.GRID_HEIGHT

		# Draw horizontal and vertical lines
		for x in range(1, self.GRID_WIDTH):
			self.c.line((x*step_width, 0, x*step_width, self.c.height))

			for y in range(1, self.GRID_HEIGHT):
				self.c.line((0, y*step_height, self.c.width, y*step_height))

		# Draw the app names
		for index, item in enumerate(self.el.contents):
			app_name = self.el.contents[index][0]
			text_bounds = self.c.get_text_bounds(app_name)

			x_cord = (index%self.GRID_WIDTH)*step_width+(step_width-text_bounds[0])/2
			y_cord = (index//self.GRID_HEIGHT)*step_height+(step_height-text_bounds[1])/2

			self.c.text(app_name, (x_cord, y_cord))

		# Invert the selected cell
		selected_x = (item_x)*step_width
		selected_y = (item_y)*step_height
		self.c.invert_rect((selected_x, selected_y, selected_x+step_width, selected_y+step_height))

		self.c.display()

	def refresh(self):
		self.draw_grid()
