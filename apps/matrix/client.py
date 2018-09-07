import sys

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

class Client():

	def __init__(self, username, password):
		self.client = MatrixClient("https://matrix.org")

		try:
			self.client.login_with_password(username, password)

		except MatrixRequestError as e:
			print(e)
			if e.code == 403:
				print("Wrong username or password")
				sys.exit(4)
			else:
				print("Check server details")
				sys.exit(2)

		except MissingSchema as e:
			print("Bad URL format")
			print(e)
			sys.exit(3)

		print("Logged in")

	def updateDisplayName(self):
		try:
			self.user = self.client.get_user("@%s:matrix.org" % self.username)

			return self.user.get_display_name()

		except MatrixRequestError as e:
			print(e)
			if e.code == 400:
				print("User ID/Alias in the wrong format")
				sys.exit(11)

	def updateRooms(self):
		try:
			self.rooms = self.client.get_rooms()

			return self.rooms

		except MatrixRequestError as e:
			print(e)
			print("Error occured while getting rooms")
			sys.exit(12)
