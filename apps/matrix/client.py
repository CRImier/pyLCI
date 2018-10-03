from libs.matrix_client.matrix_client.client import MatrixClient
from libs.matrix_client.matrix_client.api import MatrixRequestError
from libs.matrix_client.matrix_client.user import User
from requests.exceptions import MissingSchema

class Client():

	def __init__(self, username, logger, password=None, token=None):
		self.logger = logger

		self.username = username
		self.token = None
		self.logged_in = True

		# Create the matrix client
		if token == None and password != None:
			self.matrix_client = MatrixClient("https://matrix.org")

			# Try logging in the user
			try:
				self.token = self.matrix_client.login(username=username, password=password)
				self.user = User(self.matrix_client, self.matrix_client.user_id)

			except MatrixRequestError as e:
				self.logged_in = False
				self.logger.error(e)
				if e.code == 403:
					self.logger.error("Wrong username or password")
				else:
					self.logger.error("Check server details")

			except MissingSchema as e:
				self.logger.exception("Bad URL format")

		else:
			self.matrix_client = MatrixClient("https://matrix.org", token=token, user_id=username)
			self.user = User(self.matrix_client, self.matrix_client.user_id)

	# Return the user's display name
	def get_user_display_name(self):
		return self.user.get_display_name()

	# Get the rooms of the user
	def get_rooms(self):
		return self.matrix_client.rooms

	def get_user(self):
		return self.user

	def get_token(self):
		return self.token
