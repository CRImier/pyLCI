from apps import ZeroApp
from ui import DatePicker

class CalendarApp(ZeroApp):

	menu_name = "Calendar"

	def on_start(self):
		DatePicker(self.i, self.o)