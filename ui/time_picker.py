from time import sleep

from base_ui import BaseUIElement
from canvas import Canvas

class TimePicker(BaseUIElement):

	def __init__(self, i, o, name="TimePicker"):

		BaseUIElement.__init__(self, i, o, name)

		self.c = Canvas(self.o)
		self.font = self.c.load_font("Fixedsys62.ttf", 32)

		self.currentHour = 12
		self.currentMinute = 0

	def get_return_value(self):
		pass

	def generate_keymap(self):
		return {
			"KEY_RIGHT": "move_right",
			"KEY_LEFT": "move_left",
			"KEY_ENTER": "accept_value",
			"KEY_F1": "exit_time_picker"
		}

	def move_right(self):
		pass

	def move_left(self):
		pass

	def idle_loop(self):
		sleep(0.1)

	def exit_time_picker(self):
		self.deactivate()

	def accept_value(self):
		pass

	def draw_clock(self):
		self.c.clear()

		clock_string = "{:02d}:{:02d}".format(self.currentHour, self.currentMinute)

		centered_cords = self.c.get_centered_text_bounds(clock_string, font=self.font)

		self.c.text(clock_string, (centered_cords[0], centered_cords[1]), font=self.font)

		self.c.display()

	def refresh(self):
		self.draw_clock()