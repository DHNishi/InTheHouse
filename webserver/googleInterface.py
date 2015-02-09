import requests

URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

class ApiInterface(object):
	token = None
	def __init__(self, token):
		self.token = token

	def getEmail(self):
		return self.getJSON()['email']

	def getId(self):
		return self.getJSON()['id']

	def getJSON(self):
		return requests.get(URL, headers={'Authorization': 'Bearer ' + self.token}).json()
