from base_ui import BaseUIElement
from canvas import Canvas

class DatePicker(BaseUIElement):

	def __init__(self, i, o, name="DatePicker"):

		BaseUIElement.__init__(self, i, o, name)

		self.c = Canvas(self.o)
		self.selected_option = (0, 0)

		self.draw_calendar()
	
	def generate_keymap(self):
		return {
			"KEY_RIGHT": "move_right",
			"KEY_LEFT": "move_left",
			"KEY_UP": "move_up",
			"KEY_DOWN": "move_down",
			"KEY_ENTER": "accept_value"
		}

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

		step_width = self.c.width/8
		for x in range(step_width, self.c.width, step_width):
			self.c.line((x, 0, x, self.c.height))

		self.c.display()

	def refresh(self):
		self.draw_calendar()

