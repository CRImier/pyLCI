from apps import ZeroApp
from ui import DatePicker, TimePicker

class CalendarApp(ZeroApp):

	menu_name = "Calendar"

	def on_start(self):
		self.tp = TimePicker(self.i, self.o)
		print(self.tp.activate())