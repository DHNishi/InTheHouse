import requests

URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

class ApiInterface(object):
	token = None
	JSON = None

	def __init__(self, token):
		self.token = token
		self.JSON = requests.get(URL, headers={'Authorization': 'Bearer ' + self.token}).json()
		if 'error' in self.JSON:
			raise AuthException(self.JSON)

	def getEmail(self):
		return self.JSON['email']

	def getId(self):
		return self.JSON['id']

	def getName(self):
		return self.JSON['name']

	def getPicture(self):
		return self.JSON['picture']

	def getJSON(self):
		return self.JSON

class AuthException(Exception):
	def __init__(self, json):
		self.json = json
