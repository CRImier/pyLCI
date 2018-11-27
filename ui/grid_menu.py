from time import sleep
from math import ceil

from menu import Menu
from canvas import Canvas

class GridMenu(Menu):

	cols = 3
	rows = 3

	def __init__(self, contents, i, o, rows=3, cols=3, name=None, **kwargs):

                self.rows = rows
                self.cols = cols
		Menu.__init__(self, contents, i, o, name=name, override_left=False, **kwargs)

	def generate_keymap(self):
		keymap = Menu.generate_keymap(self)
                keymap.update({
			"KEY_RIGHT": "move_down",
			"KEY_LEFT": "move_up",
			"KEY_UP": "grid_move_up",
			"KEY_DOWN": "grid_move_down",
			"KEY_ENTER": "select_entry",
			"KEY_F1": "deactivate"
		})
                return keymap

	def grid_move_up(self):
		Menu.page_up(self, counter=self.cols)

	def grid_move_down(self):
		Menu.page_down(self, counter=self.cols)


class GridViewMixin(object):

	def get_entry_count_per_screen(self):
		return self.el.cols*self.el.rows

	def draw_grid(self):
		contents = self.el.get_displayed_contents()
		pointer = self.el.pointer
                c = Canvas(self.o)
                print("P: {} FDE: {}".format(self.el.pointer, self.first_displayed_entry))
		c.clear()

		# Calculate margins
		step_width = c.width / self.el.cols
		step_height = c.height / self.el.rows

		# Calculate grid index
		item_x = pointer%self.el.cols
		item_y = pointer//self.el.rows

		# Draw horizontal and vertical lines
		for x in range(1, self.el.cols):
			c.line((x*step_width, 0, x*step_width, c.height))

			for y in range(1, self.el.rows):
				c.line((0, y*step_height, c.width, y*step_height))

		# Draw the app names
		for index, item in enumerate(self.el.contents[self.first_displayed_entry*self.el.cols:]):
			app_name = contents[index+self.first_displayed_entry*self.el.cols][0]
			text_bounds = c.get_text_bounds(app_name)

			x_cord = (index%self.el.cols)*step_width+(step_width-text_bounds[0])/2
			y_cord = (index//self.el.rows)*step_height+(step_height-text_bounds[1])/2
			c.text(app_name, (x_cord, y_cord))

		# Invert the selected cell
		selected_x = (item_x)*step_width
		selected_y = (item_y)*step_height
		c.invert_rect((selected_x, selected_y, selected_x+step_width, selected_y+step_height))

		return c.get_image()

	def refresh(self):
		self.fix_pointers_on_refresh()
		self.o.display_image(self.draw_grid())


GridMenu.view_mixin = GridViewMixin
