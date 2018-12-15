from apps import ZeroApp
from ui import Listbox, rfa

class WifiCountry(ZeroApp):

	menu_name = "WiFi Country"

	def __init__(self, *args, **kwargs):
	 	ZeroApp.__init__(self, *args, **kwargs)

	def on_start(self):

	 	with open('/usr/share/zoneinfo/iso3166.tab') as f:
	 		content = f.readlines()

	 	mc = []


	 	for l in content:
	 		# Replace tabs with spaces
	 		l = l.replace('\t', ' ')
	 		print(l)
	 		# Don't add commented lines to the listbox
	 		if l.startswith("#"):
	 			continue
	 		mc.append([rfa(l, replace_characters={}), l])

	 	lb = Listbox(mc, self.i, self.o, "WiFi country selection listbox").activate()

