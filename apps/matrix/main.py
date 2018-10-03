"""
To use this some additional things have to be installed:

- The Olm C library: Either from source or via a package manager
- Additional E2E dependencies: Run the following command
	pip install -e 'git+https://github.com/Zil0/matrix-python-sdk@e2e_beta_2#egg=matrix-python-sdk-e2e[e2e]' --process-dependency-links
	This command clones the repo and installs some things

More information: https://github.com/matrix-org/matrix-python-sdk/issues/100#issuecomment-402508438
"""


from time import sleep, strftime, localtime
from textwrap import wrap

from apps import ZeroApp
from ui import Listbox, PrettyPrinter, NumpadCharInput, Menu, LoadingIndicator, TextReader, UniversalInput, MessagesMenu
from helpers import setup_logger, read_or_create_config, local_path_gen, save_config_method_gen

from client import Client

local_path = local_path_gen(__name__)

class MatrixClientApp(ZeroApp):

	menu_name = "Matrix Client"
	default_config = '{"user_id":"undefined", "token":"undefined"}'
	config_filename = "config.json"
	
	def on_start(self):
		self.stored_messages = {}
		self.messages_menu = None
		self.active_room = ""

		self.logger = setup_logger(__name__, "info")

		self.config = read_or_create_config(local_path(self.config_filename), self.default_config, self.menu_name+" app")
		self.save_config = save_config_method_gen(self, local_path(self.config_filename))

		if not self.login():
			return False

		self.display_rooms()

	# Login the user
	def login(self):
		# Check whether the user has been logged in before
		if self.config['user_id'] != 'undefined' and self.config['token'] != 'undefined':
			self.logger.debug("User has been logged in before")

			with LoadingIndicator(self.i, self.o, message="Starting ..."):
				self.client = Client(self.config['user_id'], self.logger, token=self.config['token'])

		else:

			# Get the required user data
			username = UniversalInput(self.i, self.o, message="Enter username", name="username_dialog").activate()
			if username == "":
				return False

			# Create a matrix user id from the username, currently only ids on matrix.org are possible
			username = "@{}:matrix.org".format(username)

			password = UniversalInput(self.i, self.o, message="Enter password", name="password_dialog").activate()
			if password == "":
				return False

			# Show a beatufil loading animation while setting everything up
			with LoadingIndicator(self.i, self.o, message="Logging in ..."):
				self.client = Client(username, self.logger, password=password)

				# Store username and token
				if self.client.logged_in:
					self.config['user_id'] = username
					self.config['token'] = self.client.get_token()
					self.save_config()

					self.logger.info("Succesfully logged in")

		# Get the users rooms
		self.rooms = self.client.get_rooms()

		# Add a listener for new events to all rooms the user is in
		for r in self.rooms:
			self.rooms[r].add_listener(self._on_message)
			self.stored_messages[r] = {}

			# Used to store data for each event
			self.stored_messages[r]["events"] = []

		# Start a new thread for the listeners, waiting for events to happen
		self.client.matrix_client.start_listener_thread()

		return True
		
	# Displays a list of all rooms the user is in
	def display_rooms(self):
		menu_contents = []
		for r in self.rooms:
			current_room = self.rooms[r]

			# Count the amount of backfilled messages for each room
			self.stored_messages[current_room.room_id]["backfilled"] = 0

			# Get the last 10 messages for each room and update stored_messages
			for e in reversed(current_room.get_events()):
				self._on_message(current_room, e)
				# self.stored_messages[current_room.room_id]["backfilled"] += 1

			# Add an 'E' to the name of encrypted rooms
			room_name = "E " if current_room.encrypted else ""
			room_name += current_room.display_name

			# Enter 		-> Read messages in room
			# Right arrow 	-> Write message to room
			menu_contents.append([
				room_name,
				lambda x=current_room: self.display_messages(x),
				lambda x=current_room: self.write_message(x)
			])

		Menu(menu_contents, self.i, self.o).activate()

	# Creates a new screen with an Input to write a message
	def write_message(self, room):
		message = UniversalInput(self.i, self.o, message="Message", name="message_dialog").activate()
		if message is None:
			return False

		# Send the message to the room and display it for a short amount of time
		room.send_text(message)

	# Display all messages of a specific room
	def display_messages(self, room):
		self.logger.debug("Viewing room: {}".format(room.display_name))

		# Set the currently active room to this room, important for adding messages and refreshing the menu
		self.active_room = room.room_id

		cb = lambda x=room: self._handle_messages_top(x)

		# Create a menu to display the messages
		self.messages_menu = MessagesMenu(self._get_messages_menu_contents(room.room_id), self.i, self.o, name="matrix_messages_menu", 
			entry_height=1, top_callback=lambda x=room: self._handle_messages_top(x))

		self.messages_menu.activate()

	# Displays a single message fully with additional information (author, time)
	def display_single_message(self, msg, author, unix_time):
		full_msg = "{0}\n{1}\n\n".format(strftime("%m-%d %H:%M", localtime(unix_time / 1000)), author)

		for line in wrap(msg, 24):
			full_msg += line
			full_msg += "\n"

		TextReader(full_msg, self.i, self.o).activate()

	# Used as callback for the room listeners
	def _on_message(self, room, event):
		self.logger.debug("New event: {}".format(event['type']))

		event_type = event.get('type', "not_a_defined_event")

		# Check if a user joined the room
		if event_type == "m.room.member":
			if event.get('membership', None) == "join":

				self._add_new_message(room.room_id, {
						'timestamp': event['origin_server_ts'],
						'type': event['type'],
						'sender': unicode(event['sender']),
						'content': unicode("{} joined".format(event['content']['displayname'])),
						'id': event['event_id']
					})

		# Check for new messages
		elif event_type == "m.room.message":
			if event['content']['msgtype'] == "m.text":
				prefix = ""
				if event['sender'] == self.client.get_user().user_id:
					# Prefix own messages with a '*'
					prefix = "* "

				self._add_new_message(room.room_id, {
						'timestamp': event['origin_server_ts'],
						'type': event['type'],
						'sender': unicode(event['sender']),
						'content': unicode(prefix + event['content']['body']),
						'id': event['event_id']
					})

		elif event_type == "not_a_defined_event":
			self.logger.warning("Undefined event")

		# Update the current view if required
		if self.active_room == room.room_id:
			self.messages_menu.set_contents(self._get_messages_menu_contents(room.room_id))
			self.messages_menu.refresh()

	def _add_new_message(self, room_id, new_message):
		# Check whether it's a duplicate
		for m in self.stored_messages[room_id]['events']:
			if m['id'] == new_message['id']:
				return

		self.stored_messages[room_id]['events'].append(new_message)

	# Uses stored_messages to create a suitable list of menu entries for MessagesMenu
	def _get_messages_menu_contents(self, room_id):
		# Sort messages by their timestamp
		sorted_messages = sorted(self.stored_messages[room_id]['events'], key=lambda k: k['timestamp'])

		menu_contents = []

		for message in sorted_messages:
			menu_contents.append([message['content'], lambda c=message['content'], s=message['sender'], t=message['timestamp']: self.display_single_message(c, s, t)])

		return menu_contents

	# Callback for MessagesMenu
	def _handle_messages_top(self, room):
		messages_to_load = 5

		room.backfill_previous_messages(limit=self.stored_messages[room.room_id]["backfilled"]+5, reverse=True, num_of_messages=messages_to_load)
		self.stored_messages[room.room_id]["backfilled"] += messages_to_load



