from apps import ZeroApp
from ui import DatePicker, TimePicker

class CalendarApp(ZeroApp):

	menu_name = "Calendar"

	def on_start(self):
		self.dp = DatePicker(self.i, self.o)
		print(self.dp.activate())
