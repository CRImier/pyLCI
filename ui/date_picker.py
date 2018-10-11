import calendar
from datetime import datetime
from time import sleep

from base_ui import BaseUIElement
from canvas import Canvas

class DatePicker(BaseUIElement):

	# Grid dimensions
	GRID_WIDTH = 7
	GRID_HEIGHT = 5

	MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

	def __init__(self, i, o, name="DatePicker"):

		BaseUIElement.__init__(self, i, o, name)

		self.c = Canvas(self.o)

		# Attributes to store the current values
		self.current_month = 1
		self.current_year = 2018
		self.starting_weekday = 1

		# Top-left cell is (1, 1)
		self.selected_option = {'x': 1, 'y': 1}
		self.calendar_grid = []

		self.accepted_value = False

		self.cal = calendar.Calendar()

		# Set month and year to current month/year
		self._set_month_year(datetime.now().month, datetime.now().year)

	def get_return_value(self):
		if self.accepted_value:
			return {
				'month': self.current_month,
				'year': self.current_year,
				'date': self.calendar_grid[self.selected_option['x']-1+(self.selected_option['y']-1)*self.GRID_WIDTH]
			}
		else:
			return None
	
	def generate_keymap(self):
		return {
			"KEY_RIGHT": "move_right",
			"KEY_LEFT": "move_left",
			"KEY_UP": "move_up",
			"KEY_DOWN": "move_down",
			"KEY_ENTER": "accept_value",
			"KEY_PAGEUP": "next_month",
			"KEY_PAGEDOWN": "previous_month",
			"KEY_F1": "exit_date_picker"
		}

	def idle_loop(self):
		sleep(0.1)

	def exit_date_picker(self):
		self.deactivate()

	# Move the cursor around
	def move_right(self):
		self._move_cursor(1, 0)

	def move_left(self):
		self._move_cursor(-1, 0)

	def move_up(self):
		self._move_cursor(0, -1)

	def move_down(self):
		self._move_cursor(0, 1)

	# Switch between months - TODO
	def next_month(self):
		if self.current_month < 12:
			self._set_month_year(self.current_month+1, self.current_year)
		elif self.current_month == 12:
			self._set_month_year(1, self.current_year+1)
		else:
			self.logger.error("Weird month value: {}".format(self.current_month))

	def previous_month(self):
		if self.current_month > 1:
			self._set_month_year(self.current_month-1, self.current_year)
		elif self.current_month == 1:
			self._set_month_year(12, self.current_year-1)
		else:
			self.logger.error("Weird month value: {}".format(self.current_month))

	# Accept the currently selected value - TODO
	def accept_value(self):
		self.accepted_value = True
		self.deactivate()

	def draw_calendar(self):
		self.c.clear()

		# Create the year - month header string
		year_month = "{} - {}".format(self.MONTH_NAMES[self.current_month-1], self.current_year)

		# Draw 'year - month' centered at the top of the screen
		month_year_text_bounds = self.c.get_text_bounds(year_month)
		centered_cords = self.c.get_centered_text_bounds(year_month)
		self.c.text(year_month, (centered_cords[0], 0))

		# Draw calendar grid
		# Calculate margin between vertical/horizontal lines
		step_width = self.c.width / self.GRID_WIDTH
		step_height = (self.c.height - month_year_text_bounds[1]) / self.GRID_HEIGHT

		# Draw lines
		for x in range(step_width, self.c.width-step_width, step_width):
			self.c.line((x+1, month_year_text_bounds[1], x+1, step_height*6))

			for y in range(step_height, self.c.height, step_height):
				self.c.line((0, y, self.c.width, y))

		# Draw dates
		i = self.starting_weekday
		for date in self.calendar_grid:
			if date == -1:
				continue

			# Jump to the first line if it's reached the last cell
			if i >= self.GRID_WIDTH * self.GRID_HEIGHT:
				i = 0

			date_text_bounds = self.c.get_text_bounds(str(date))

			# Calculate the coordinates for the date string
			x_cord = (i%self.GRID_WIDTH)*step_width+((step_width-date_text_bounds[0])/2)
			y_cord = (i//self.GRID_WIDTH)*step_height+step_height+((step_height-date_text_bounds[1])/2)


			self.c.text(str(date), (x_cord+1, y_cord+1))

			# Increase the counter and continue to the next date, import for positioning
			i += 1

		# Highlight selected option
		selected_x = (self.selected_option['x']-1)*step_width
		selected_y = (self.selected_option['y']-1)*step_height+step_height
		self.c.invert_rect((selected_x+1, selected_y+1, selected_x+step_width+1, selected_y+step_height))

		self.c.display()

	def refresh(self):
		self.draw_calendar()

	# Moves the cursor
	def _move_cursor(self, delta_x, delta_y):
		if self._check_movable_field(self.selected_option['x']+delta_x, self.selected_option['y']+delta_y):
			self.selected_option['x'] += delta_x
			self.selected_option['y'] += delta_y
			self.refresh()

	# Check whether the desired movement is viable
	def _check_movable_field(self, new_x, new_y):
		# New movement would definitely be out of grid
		if (new_x-1)+(new_y-1)*self.GRID_WIDTH >= len(self.calendar_grid):
			return False

		if (	 self.calendar_grid[(new_x-1)+(new_y-1)*self.GRID_WIDTH] != -1
			 and new_x <= self.GRID_WIDTH
			 and new_x >= 1
			 and new_y <= self.GRID_HEIGHT
			 and new_y >= 1):

			return True
		else:
			return False

	# Set the current mont/year to display
	def _set_month_year(self, month, year):
		# Set new month and year
		self.current_month = month
		self.current_year = year

		# Clear the calendar grid
		self.calendar_grid = []

		# Get the weekday of the first day of the month
		first_day, _ = calendar.monthrange(self.current_year, self.current_month)
		self.starting_weekday = first_day

		i = 0
		# Assign -1 to empty cells
		for i in range(first_day):
			self.calendar_grid.append(-1)

		# Set the cursor to the first viable cell
		self.selected_option['x'] = i+2

		i = first_day
		for date in self.cal.itermonthdays(self.current_year, self.current_month):
			if date == 0:
				continue

			self.calendar_grid.append(date)

			i += 1

		# Assign -1 to empty cells
		for i in range(self.GRID_WIDTH*self.GRID_HEIGHT-i):
			self.calendar_grid.append(-1)

		self.refresh()



