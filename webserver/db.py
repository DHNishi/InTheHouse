import pymongo
import time

class DbInstance(object):
	client = None
	db = None
	users = None
	friendRequests = None

	def connect(self, host, uname, paswd):
		super(DbInstance, self).__init__()
		self.client = pymongo.MongoClient(host)
		self.db = self.client["inthehouse"]
		self.users = self.db["users"]
		self.friendRequests = self.db["friendRequests"]
		if not self.db.authenticate(uname, paswd):
			print "Auth error."
			raise Exception("Auth exception")

	def __init__(self, host, uname, paswd):
		self.connect(host, uname, paswd)

	def checkin(self, id, email, name):
		now = str(int(time.time()))
		result = self.users.find_one( {'id': id} )
		self.users.update( {'id':id}, {'$set': {'id':id, 'email': email, 'name': name, 'checkin': now} }, True )

	def getFriends(self, id):
		user = self.users.find_one( {'id':id} )
		result = []
		now = int(time.time())
		if 'friends' in user:
			for friend in user['friends']:
				friend = self.findUserById(friend)
				del friend['_id']
				if 'friends' in friend:
					del friend['friends']
				friend['checkin'] = str(now - int(friend['checkin']))
				result.append(friend)
		return result

	def findUserById(self, id):
		return self.users.find_one( {"id":id} )

	def findUserByEmail(self, email):
		return self.users.find_one( {"email":email} )

	def requestFriend(self, id, friendEmail):
		friend = self.findUserByEmail(friendEmail)
		if (friend == None):
			raise FriendNotFoundException
		self.friendRequests.insert( {"from": id, "to": friend["id"]} )

class FriendNotFoundException(Exception):
	def __init__(self):
		pass

class AuthException(Exception):
	def __init__(self):
		pass
