from libs.matrix_client.matrix_client.client import MatrixClient
from libs.matrix_client.matrix_client.api import MatrixRequestError
from libs.matrix_client.matrix_client.user import User
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
			self.user = User(self.matrix_client, self.matrix_client.user_id)

		except MatrixRequestError as e:
			self.logger.error(e)
			if e.code == 403:
				self.logger.error("Wrong username or password")
			else:
				self.logger.error("Check server details")

		except MissingSchema as e:
			self.logger.exception("Bad URL format")

	# Return the user's display name
	def get_user_display_name(self):
		return self.user.get_display_name()

	# Get the rooms of the user
	def get_rooms(self):
		return self.matrix_client.rooms

	def get_user(self):
		return self.user
