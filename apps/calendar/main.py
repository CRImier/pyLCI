from apps import ZeroApp
from ui import DatePicker, TimePicker

def test_callback():
	print("hello world")

class CalendarApp(ZeroApp):

	menu_name = "Calendar"

	def on_start(self):
		self.dp = DatePicker(self.i, self.o, s_year=2015, callback=test_callback)
		print(self.dp.activate())
