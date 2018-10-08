import calendar
from time import sleep

from base_ui import BaseUIElement
from canvas import Canvas

class DatePicker(BaseUIElement):

	# Grid dimensions
	GRID_WIDTH = 7
	GRID_HEIGHT = 5

	def __init__(self, i, o, name="DatePicker"):

		BaseUIElement.__init__(self, i, o, name)

		self.c = Canvas(self.o)

		# Top-left cell is (1, 1)
		self.selected_option = {'x': 1, 'y': 1}

		self.year_month = "2018 - Oct"
		self.calendar_grid = []

		self.cal = calendar.Calendar()
	
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
		if self.selected_option['x'] < self.GRID_WIDTH:
			if self._check_movable_field(self.selected_option['x']+1, self.selected_option['y']):
				self.selected_option['x'] += 1
				self.refresh()

		elif self.selected_option['x'] == self.GRID_WIDTH and self.selected_option['y'] < self.GRID_HEIGHT:
			if self._check_movable_field(1, self.selected_option['y']+1):
				self.selected_option['x'] = 1
				self.selected_option['y'] += 1
				self.refresh()

	def move_left(self):
		if self.selected_option['x'] > 1:
			if self._check_movable_field(self.selected_option['x']-1, self.selected_option['y']):
				self.selected_option['x'] -= 1
				self.refresh()

		elif self.selected_option['x'] == 1 and self.selected_option['y'] > 1:
			if self._check_movable_field(1, self.selected_option['y']-1):
				self.selected_option['x'] = self.GRID_WIDTH
				self.selected_option['y'] -= 1
				self.refresh()

	def move_up(self):
		if self.selected_option['y'] > 1:
			if self._check_movable_field(self.selected_option['x'], self.selected_option['y']-1):
				self.selected_option['y'] -= 1
				self.refresh()

		elif self.selected_option['y'] == 1:
			if self._check_movable_field(self.selected_option['x'], self.GRID_HEIGHT):
				self.selected_option['y'] = self.GRID_HEIGHT
				self.refresh()
			else:
				self.selected_option['y'] = self.GRID_HEIGHT-1
				self.refresh()

	def move_down(self):
		if self.selected_option['y'] < self.GRID_HEIGHT:
			if self._check_movable_field(self.selected_option['x'], self.selected_option['y']+1):
				self.selected_option['y'] += 1
				self.refresh()
			else:
				self.selected_option['y'] = 1
				self.refresh()

		elif self.selected_option['y'] == self.GRID_HEIGHT:
			if self._check_movable_field(self.selected_option['x'], 1):
				self.selected_option['y'] = 1
				self.refresh()

	def accept_value(self):
		pass

	def draw_calendar(self):
		self.c.clear()

		# Draw 'year - month' at the top
		month_year_text_bounds = self.c.get_text_bounds(self.year_month)
		centered_cords = self.c.get_centered_text_bounds(self.year_month)
		self.c.text(self.year_month, (centered_cords[0], 0))

		# Draw calendar grid
		step_width = self.c.width / self.GRID_WIDTH
		step_height = (self.c.height - month_year_text_bounds[1]) / self.GRID_HEIGHT

		for x in range(step_width, self.c.width-step_width, step_width):
			self.c.line((x+1, month_year_text_bounds[1], x+1, step_height*6))

			for y in range(step_height, self.c.height, step_height):
				self.c.line((0, y, self.c.width, y))

		# Draw dates
		first_day, _ = calendar.monthrange(2018, 10)

		# Assign -1 to empty cells
		for i in range(first_day):
			self.calendar_grid.append(-1)

		i = first_day
		for date in self.cal.itermonthdays(2018, 10):
			if date == 0:
				continue

			self.calendar_grid.append(date)

			date_text_bounds = self.c.get_text_bounds(str(date))

			x_cord = (i%self.GRID_WIDTH)*step_width+((step_width-date_text_bounds[0])/2)
			y_cord = (i//self.GRID_WIDTH)*step_height+step_height+((step_height-date_text_bounds[1])/2)

			self.c.text(str(date), (x_cord+1, y_cord+1))

			i += 1

		# Assign -1 to empty cells
		for i in range(self.GRID_WIDTH*self.GRID_HEIGHT-i):
			self.calendar_grid.append(-1)

		# Highlight selected option
		selected_x = (self.selected_option['x']-1)*step_width
		selected_y = (self.selected_option['y']-1)*step_height+step_height
		self.c.invert_rect((selected_x+1, selected_y+1, selected_x+step_width+1, selected_y+step_height))

		self.c.display()

	def refresh(self):
		self.draw_calendar()

	# Check for empty cells
	def _check_movable_field(self, x, y):
		if self.calendar_grid[(x-1)+(y-1)*self.GRID_WIDTH] != -1:
			return True
		else:
			return False

