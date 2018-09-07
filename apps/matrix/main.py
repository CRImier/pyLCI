from apps import ZeroApp
from ui import CharArrowKeysInput, Listbox, PrettyPrinter, NumpadCharInput, Menu, LoadingIndicator, TextReader

from time import sleep, strftime, localtime
from textwrap import wrap

from client import Client

class MatrixClientApp(ZeroApp):

	menu_name = "Matrix Client"
	
	def on_start(self):
		self.stored_messages = []
		self.messages_menu = None

		self.login()
		self.displayRooms()

	def login(self):
		username = NumpadCharInput(self.i, self.o, message="Enter username", name="username_dialog").activate()
		if username is None:
			return False

		print(username)

		password = NumpadCharInput(self.i, self.o, message="Enter password", name="password_dialog").activate()
		if password is None:
			return False

		print(password)

		with LoadingIndicator(self.i, self.o, message="Logging in ..."):
			self.client = Client(username, password)
		
	def displayRooms(self):
		# Get all rooms the user is in
		rooms = self.client.updateRooms()

		# Create a list of rooms to choose from
		lc = []
		for r in rooms:
			lc.append([rooms[r].display_name, r])

		chosenRoom = Listbox(lc, self.i, self.o, name="Room menu").activate()

		if not chosenRoom:
			return False

		self.choose_room_action(rooms[chosenRoom])

	def write_message(self, room):
		message = NumpadCharInput(self.i, self.o, message="Message", name="message_dialog").activate()
		if message is None:
			return False

		print(message)

		room.send_text(message)

		PrettyPrinter(message, self.i, self.o, 3)

	def display_messages(self, room):
		# Add a listener to the room and provide a callback
		room.add_listener(self._on_message)
		self.client.client.start_listener_thread()

		# Create a menu in which the messages are displayed
		self.messages_menu = Menu(self.stored_messages, self.i, self.o, name="matrix_messages_menu", entry_height=1)
		self.messages_menu.activate()

	def display_single_message(self, msg, author, unix_time):
		full_msg = "{0}\n{1}\n\n".format(strftime("%m-%d %H:%M", localtime(unix_time / 1000)), author)

		for line in wrap(msg, 24):
			full_msg += line
			full_msg += "\n"

		TextReader(full_msg, self.i, self.o).activate()

	def choose_room_action(self, room):
		menu_contents = [
			["Write message", lambda: self.write_message(room)],
			["Read messages", lambda: self.display_messages(room)]
		]

		Menu(menu_contents, self.i, self.o, "Choose action").activate()

	def _on_message(self, room, event):
		print("New event: %s" % event['type'])
		print(event.keys())
		print(event['content'].keys())
		print(event['origin_server_ts'])

		# Check if a new user joined the room
		if event['type'] == "m.room.member":
			if event['membership'] == "join":
				self.stored_messages.append(["{0} joined".format(event['content']['displayname'])])
				print("{0} joined".format(event['content']['displayname']))

		# Check for new messages
		elif event['type'] == "m.room.message":
			if event['content']['msgtype'] == "m.text":
				self.stored_messages.append([event['content']['body'],
					lambda: self.display_single_message(event['content']['body'], event['sender'], event['origin_server_ts'])])

				print("New message: %s wrote: %s" % (event['sender'], event['content']['body']))

		# Update the contents of the menu and refresh it
		self.messages_menu.set_contents(self.stored_messages)
		self.messages_menu.refresh()


