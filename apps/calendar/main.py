from apps import ZeroApp
from ui import DatePicker, TimePicker

def test_callback(ul):
	print(ul)

class CalendarApp(ZeroApp):

	menu_name = "Calendar"

	def on_start(self):
		self.dp = DatePicker(self.i, self.o, callback=test_callback, strftime_format="%Y-%m-%d %H:%M:%S")
		print(self.dp.activate())
