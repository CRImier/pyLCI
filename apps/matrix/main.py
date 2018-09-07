from apps import ZeroApp
from ui import CharArrowKeysInput, Listbox, PrettyPrinter, NumpadCharInput, Menu, LoadingIndicator, TextReader

from time import sleep, strftime, localtime
from textwrap import wrap

from client import Client

class MatrixClientApp(ZeroApp):

	menu_name = "Matrix Client"
	
	def on_start(self):
		self.stored_messages = {}
		self.messages_menu = None
		self.active_room = ""

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

		# Add a listener to all rooms the user is in
		self.rooms = self.client.updateRooms()

		for r in self.rooms:
			self.rooms[r].add_listener(self._on_message)

			self.stored_messages[r] = []

		self.client.client.start_listener_thread()
		
	def displayRooms(self):
		menu_contents = []
		for r in self.rooms:
			current_room = self.rooms[r]

			print(current_room.display_name)

			menu_contents.append([
				current_room.display_name,
				lambda x=current_room: self.display_messages(x),
				lambda x=current_room: self.write_message(x)
			])

		Menu(menu_contents, self.i, self.o).activate()

	def write_message(self, room):
		message = NumpadCharInput(self.i, self.o, message="Message", name="message_dialog").activate()
		if message is None:
			return False

		room.send_text(message)
		PrettyPrinter(message, self.i, self.o, 1)

	def display_messages(self, room):
		print("Viewing room: {0}".format(room.display_name))

		self.active_room = room.room_id

		print(self.stored_messages)
		for k in self.stored_messages:
			print(self.rooms[k].display_name)
			print len(self.stored_messages[k])
		# Create a menu in which the messages are displayed
		self.messages_menu = Menu(self.stored_messages[room.room_id], self.i, self.o, name="matrix_messages_menu", entry_height=1)
		self.messages_menu.activate()

		self.messages_menu.set_contents(self.stored_messages[room.room_id])
		self.messages_menu.refresh()

	def display_single_message(self, msg, author, unix_time):
		full_msg = "{0}\n{1}\n\n".format(strftime("%m-%d %H:%M", localtime(unix_time / 1000)), author)

		for line in wrap(msg, 24):
			full_msg += line
			full_msg += "\n"

		TextReader(full_msg, self.i, self.o).activate()

	def _on_message(self, room, event):
		print("New event: %s" % event['type'])
		print(event.keys())
		print(event['content'].keys())
		print(event['origin_server_ts'])

		print(room.room_id)

		# Check if a new user joined the room
		if event['type'] == "m.room.member":
			if event['membership'] == "join":
				self.stored_messages[room.room_id].append(["{0} joined".format(event['content']['displayname'])])
				print("{0} joined".format(event['content']['displayname']))

		# Check for new messages
		elif event['type'] == "m.room.message":
			if event['content']['msgtype'] == "m.text":
				self.stored_messages[room.room_id].append([event['content']['body'],
					lambda: self.display_single_message(event['content']['body'], event['sender'], event['origin_server_ts'])])

				print("New message: %s wrote: %s" % (event['sender'], event['content']['body']))

		# Update the contents of the menu and refresh it
		if self.active_room == room.room_id:
			self.messages_menu.set_contents(self.stored_messages[room.room_id])
			self.messages_menu.refresh()


