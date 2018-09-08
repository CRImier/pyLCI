from time import sleep, strftime, localtime
from textwrap import wrap

from apps import ZeroApp
from ui import Listbox, PrettyPrinter, NumpadCharInput, Menu, LoadingIndicator, TextReader
from helpers import setup_logger

from client import Client

class MatrixClientApp(ZeroApp):

	menu_name = "Matrix Client"
	
	def on_start(self):
		self.stored_messages = {}
		self.messages_menu = None
		self.active_room = ""

		self.logger = setup_logger(__name__, "info")

		self.login()
		self.display_rooms()

	# Login the user
	def login(self):
		# Get the required user data
		username = NumpadCharInput(self.i, self.o, message="Enter username", name="username_dialog").activate()
		if username is None:
			return False

		password = NumpadCharInput(self.i, self.o, message="Enter password", name="password_dialog").activate()
		if password is None:
			return False

		# Start the logging in process
		self.logger.info("Trying to log in the user")

		with LoadingIndicator(self.i, self.o, message="Logging in ..."):
			self.client = Client(username, password, self.logger)

		self.logger.info("Succesfully logged in")

		# Add a listener to all rooms the user is in
		self.rooms = self.client.updateRooms()

		self.user_name = self.client.updateDisplayName()

		for r in self.rooms:
			self.rooms[r].add_listener(self._on_message)
			self.stored_messages[r] = []

		# Start a new thread for the listeners, waiting for events to happen
		self.client.matrix_client.start_listener_thread()
		
	# Displays a list of all rooms the user is in
	def display_rooms(self):
		menu_contents = []
		for r in self.rooms:
			current_room = self.rooms[r]

			# Enter 		-> Read messages in room
			# Right arrow 	-> Write message to room
			menu_contents.append([
				current_room.display_name,
				lambda x=current_room: self.display_messages(x),
				lambda x=current_room: self.write_message(x)
			])

		Menu(menu_contents, self.i, self.o).activate()

	# Creates a new screen with an Input
	def write_message(self, room):
		message = NumpadCharInput(self.i, self.o, message="Message", name="message_dialog").activate()
		if message is None:
			return False

		# Send the message to the room and display it for a short amount of time
		room.send_text(message)
		PrettyPrinter(message, self.i, self.o, 0.5)

	# Displays all messages in a room
	def display_messages(self, room):
		self.logger.debug("Viewing room: {}".format(room.display_name))

		# Set the currently active room to this room
		self.active_room = room.room_id

		# Create a menu in which the messages are displayed
		self.messages_menu = Menu(self.stored_messages[room.room_id], self.i, self.o, name="matrix_messages_menu", entry_height=1)
		self.messages_menu.activate()

		# Set the contents of the menu to the messages for this room and refresh it
		self.messages_menu.set_contents(self.stored_messages[room.room_id])
		self.messages_menu.refresh()

	# Displays a single message fully with additional information (author, time)
	def display_single_message(self, msg, author, unix_time):
		full_msg = "{0}\n{1}\n\n".format(strftime("%m-%d %H:%M", localtime(unix_time / 1000)), author)

		for line in wrap(msg, 24):
			full_msg += line
			full_msg += "\n"

		TextReader(full_msg, self.i, self.o).activate()

	# Used as callback for the room listeners
	def _on_message(self, room, event):
		self.logger.info("New event: {}".format(event['type']))

		# Check if a new user joined the room
		if event['type'] == "m.room.member":
			if event['membership'] == "join":
				self.stored_messages[room.room_id].append(["{0} joined".format(event['content']['displayname'])])

		# Check for new messages
		elif event['type'] == "m.room.message":
			if event['content']['msgtype'] == "m.text":
				prefix = ""
				if event['sender'] == self.client.get_user().user_id:
					prefix = "* "

				self.stored_messages[room.room_id].append([prefix + event['content']['body'],
					lambda: self.display_single_message(event['content']['body'], event['sender'], event['origin_server_ts'])])

		# Update the contents of the menu and refresh it
		if self.active_room == room.room_id:
			self.messages_menu.set_contents(self.stored_messages[room.room_id])
			self.messages_menu.refresh()


