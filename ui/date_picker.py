from time import sleep

from base_ui import BaseUIElement
from canvas import Canvas

class DatePicker(BaseUIElement):

	def __init__(self, i, o, name="DatePicker"):

		BaseUIElement.__init__(self, i, o, name)

		self.c = Canvas(self.o)
		self.selected_option = (0, 0)

		self.year_month = "2018 - Oct"
	
	def generate_keymap(self):
		return {
			"KEY_RIGHT": "move_right",
			"KEY_LEFT": "move_left",
			"KEY_UP": "move_up",
			"KEY_DOWN": "move_down",
			"KEY_ENTER": "accept_value"
		}

	def idle_loop(self):
		sleep(0.1)

	def move_right(self):
		self.selected_option[0] += 1
		self.refresh()

	def move_left(self):
		self.selected_option[0] -= 1
		self.refresh()

	def move_up(self):
		self.selected_option[1] -= 1
		self.refresh()

	def move_down(self):
		self.selected_option[1] += 1
		self.refresh()

	def accept_value(self):
		pass

	def draw_calendar(self):
		self.c.clear()

		# Draw year - month at the top
		month_year_text_bounds = self.c.get_text_bounds(self.year_month)
		centered_cords = self.c.get_centered_text_bounds(self.year_month)
		self.c.text(self.year_month, (centered_cords[0], 0))

		# Draw the calendar grid
		step_width = self.c.width / 8
		for x in range(step_width, self.c.width, step_width):
			self.c.line((x, month_year_text_bounds[1], x, self.c.height))

		step_height = (self.c.height - month_year_text_bounds[1]) / 4
		for y in range(step_height, self.c.height, step_height):
			self.c.line((0, y, self.c.width, y))

		self.c.display()

	def refresh(self):
		self.draw_calendar()

