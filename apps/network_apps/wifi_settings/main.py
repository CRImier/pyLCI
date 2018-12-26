from apps import ZeroApp
from ui import Menu, Listbox, LoadingBar, PrettyPrinter as Printer, rfa

from time import sleep

from pyric import pyw

class WifiCountry(ZeroApp):

	menu_name = "WiFi settings"

	def __init__(self, *args, **kwargs):
	 	ZeroApp.__init__(self, *args, **kwargs)

	def get_current_wifi_country(self):
		return pyw.regget()

	def set_wifi_country(self, code, sleep_time=1, retries=10):
		pyw.regset(code)
		counter = retries
		while code != self.get_current_wifi_country():
			counter -= 1
			sleep(sleep_time)
			if counter == 0:
				return False
		return True

	def on_start(self):
            mc = [["WiFi country", self.change_wifi_country]]
            Menu(mc, self.i, self.o, name="WiFi settings app main menu").activate()

        def change_wifi_country(self):
	 	with open('/usr/share/zoneinfo/iso3166.tab') as f:
	 		content = f.readlines()

	 	lc = []
		current_country = self.get_current_wifi_country()

	 	for l in content:
	 		# Replace tabs with spaces and strip newlines
	 		l = l.replace('\t', ' ').strip()
	 		# Filter commented-out lines
	 		if l.startswith("#"):
	 			continue
                        country_code, description = l.split(' ', 1)
	 		lc.append([rfa(l), country_code])

		choice = Listbox(lc, self.i, self.o, name="WiFi country selection listbox", selected=current_country).activate()
		if choice:
			with LoadingBar(self.i, self.o, message="Changing WiFi country", name="WiFi country change LoadingBar"):
				result = self.set_wifi_country(choice)
			if result:
				Printer("Changed the country successfully!", self.i, self.o)
			else:
				Printer("Failed to change the country!", self.i, self.o)
