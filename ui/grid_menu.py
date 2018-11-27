from time import sleep
from math import ceil

from menu import Menu
from canvas import Canvas

class GridMenu(Menu):

	cols = 3
	rows = 3

	def __init__(self, contents, i, o, rows=3, cols=3, name=None, **kwargs):

		Menu.__init__(self, contents, i, o, name=name, override_left=False, **kwargs)
                self.rows = rows
                self.cols = cols
		self.view = GridView(o, self)

	def generate_keymap(self):
		return {
			"KEY_RIGHT": "move_right",
			"KEY_LEFT": "move_left",
			"KEY_UP": "move_up",
			"KEY_DOWN": "move_down",
			"KEY_ENTER": "select_entry",
			"KEY_F1": "exit_menu"
		}

	def select_entry(self, callback_number=1):
		entry_index = self.pointer+self.y_index*self.cols
		Menu.select_entry(self, callback_number=callback_number, entry_index=entry_index)

	def exit_menu(self):
		self.deactivate()

	def move_right(self):
		self._move_cursor(1)

	def move_left(self):
		self._move_cursor(-1)

	def move_up(self):
		self._move_cursor(-self.cols)

	def move_down(self):
		self._move_cursor(self.cols)

	def refresh(self):
		self.view.refresh()

	def _move_cursor(self, m):
		self.pointer += m

		# Scroll up if y_index is larger than 0
		if self.y_index > 0 and self.pointer < 0:
			self.y_index += -1

		# Scroll down if the pointer has reached the end and there are cells left
		if self.pointer//self.cols >= self.rows:
			if self.y_index + self.rows < ceil(len(self.contents)/float(self.cols)):
				self.y_index += 1
				self.pointer += -3

		# Check whether the new cell is empty
		if self.pointer + self.y_index*self.cols >= len(self.contents):
			self.pointer -= m

		self.pointer = self.pointer%(self.cols*self.rows)
                print(self.pointer)
		self.refresh()


class GridView():

	def __init__(self, o, ui_element):
		self.c = Canvas(o)
		self.el = ui_element
		self.y_index = 0

	def draw_grid(self):
		self.c.clear()

		# Calculate margins
		step_width = self.c.width / self.el.cols
		step_height = self.c.height / self.el.rows

		# Calculate grid index
		item_x = self.el.pointer%self.el.cols
		item_y = self.el.pointer//self.el.rows

		# Draw horizontal and vertical lines
		for x in range(1, self.el.cols):
			self.c.line((x*step_width, 0, x*step_width, self.c.height))

			for y in range(1, self.el.rows):
				self.c.line((0, y*step_height, self.c.width, y*step_height))

		# Draw the app names
		for index, item in enumerate(self.el.contents[self.y_index*self.el.cols:]):
			app_name = self.el.contents[index+self.y_index*self.el.cols][0]
			text_bounds = self.c.get_text_bounds(app_name)

			x_cord = (index%self.el.cols)*step_width+(step_width-text_bounds[0])/2
			y_cord = (index//self.el.rows)*step_height+(step_height-text_bounds[1])/2
			self.c.text(app_name, (x_cord, y_cord))

		# Invert the selected cell
		selected_x = (item_x)*step_width
		selected_y = (item_y)*step_height
		self.c.invert_rect((selected_x, selected_y, selected_x+step_width, selected_y+step_height))

		self.c.display()

	def refresh(self):
		self.draw_grid()
