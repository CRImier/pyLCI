from time import sleep
from math import ceil
from copy import copy

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
        fde_increment = 3

	def get_entry_count_per_screen(self):
		return self.el.cols*self.el.rows

	def draw_grid(self):
		contents = self.el.get_displayed_contents()
		pointer = self.el.pointer
		full_entries_shown = self.get_entry_count_per_screen()
		entries_shown = min(len(contents), full_entries_shown)
		disp_entry_positions = range(self.first_displayed_entry, self.first_displayed_entry+entries_shown)
		for i in copy(disp_entry_positions):
			if i not in range(len(contents)):
				disp_entry_positions.remove(i)
                c = Canvas(self.o)
		c.clear()

		# Calculate margins
		step_width = c.width / self.el.cols
		step_height = c.height / self.el.rows

		# Calculate grid index
		item_x = (pointer-self.first_displayed_entry)%self.el.cols
		item_y = (pointer-self.first_displayed_entry)//self.el.rows

		# Draw horizontal and vertical lines
		for x in range(1, self.el.cols):
			c.line((x*step_width, 0, x*step_width, c.height))

			for y in range(1, self.el.rows):
				c.line((0, y*step_height, c.width, y*step_height))

		# Draw the app names
		for i, index in enumerate(disp_entry_positions):
			app_name = contents[index][0]
			text_bounds = c.get_text_bounds(app_name)

			x_cord = (i%self.el.cols)*step_width+(step_width-text_bounds[0])/2
			y_cord = (i//self.el.rows)*step_height+(step_height-text_bounds[1])/2
			c.text(app_name, (x_cord, y_cord))

		# Invert the selected cell
		selected_x = (item_x)*step_width
		selected_y = (item_y)*step_height
		c.invert_rect((selected_x, selected_y, selected_x+step_width, selected_y+step_height))

		return c.get_image()

	def refresh(self):
                # The following code is a dirty hack to fix navigation
                # because I need to make base_list_ui code better
                # at dealing with stuff like this. or maybe make GridViewMixin's
                # own version of fix_pointers_on_refresh?
                underflow = False
                # Moving up, this might happen - clamping FDE
                if self.first_displayed_entry > self.el.pointer:
                        self.first_displayed_entry = self.el.pointer
                        underflow = True
		self.fix_pointers_on_refresh()
                if self.first_displayed_entry:
                        # Making sure FDE is divisible by the grid width
			div, mod = divmod(self.first_displayed_entry, self.el.cols)
			self.first_displayed_entry = div*self.el.cols
                        # If we're not moving up
			if mod and not underflow:
                            self.first_displayed_entry += self.el.cols
		self.o.display_image(self.draw_grid())


GridMenu.view_mixin = GridViewMixin
