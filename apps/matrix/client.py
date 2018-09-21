import sys

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

class Client():

	def __init__(self, username, password, logger):
		# Create the matrix client
		self.matrix_client = MatrixClient("https://matrix.org", encryption=True, restore_device_id=True)
		self.logger = logger

		self.username = username

		# Try logging in the user
		try:
			self.matrix_client.login(username=username, password=password)

		except MatrixRequestError as e:
			self.logger.error(e)
			if e.code == 403:
				self.logger.error("Wrong username or password")
				sys.exit(4)
			else:
				self.logger.error("Check server details")
				sys.exit(2)

		except MissingSchema as e:
			self.logger.error(e)
			self.logger.error("Bad URL format")

			sys.exit(3)

	# Get the user's display name, store and return it
	def update_display_name(self):
		try:
			self.user = self.matrix_client.get_user("@{}:matrix.org".format(self.username))
			return self.user.get_display_name()

		except MatrixRequestError as e:
			self.logger.error(e)
			if e.code == 400:
				self.logger.error("User ID/Alias in the wrong format")

				sys.exit(11)

	# Get the rooms of the user
	def get_rooms(self):
		return self.matrix_client.rooms

	def get_user(self):
		return self.user
