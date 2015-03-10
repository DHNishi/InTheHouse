import pymongo
import time

class DbInstance(object):
	client = None
	db = None
	users = None
	friendRequests = None
	allFriends = None

	def connect(self, host, uname, paswd):
		super(DbInstance, self).__init__()
		self.client = pymongo.MongoClient(host)
		self.db = self.client["inthehouse"]
		self.users = self.db["users"]
		self.friendRequests = self.db["friendRequests"]
		self.allFriends = self.db["friends"]
		if not self.db.authenticate(uname, paswd):
			print "Auth error."
			raise Exception("Auth exception")

	def __init__(self, host, uname, paswd):
		self.connect(host, uname, paswd)

	def checkin(self, id, email, name):
		now = str(int(time.time()))
		result = self.users.find_one( {'id': id} )
		if result == None:
			self.users.insert( {'id':id, 'email': email, 'name': name, 'checkin': now} )
		else:
			self.users.update( {'id':id}, {'$set': {'checkin':now} } )

	def getFriends(self, id):
		user = self.users.find_one( {'id':id} )
		friends = self.allFriends.find( {'friend1' : id} )
		result = []
		for friend in friends:
			friend = self.findUserById(friend)
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

	def getRequests(self, id):
		requests = self.friendRequests.find( {"to": id} )
		result = []
		for request in requests:
			friend = self.findUserById(request['from'])
			result.append(friend)
		return result

	def acceptFriend(self, id, friendEmail):
		friend = self.findUserByEmail(friendEmail)
		if (friend == None):
			raise FriendNotFoundException

		self.allFriends.insert( {"friend1" : id, "friend2" : friend["id"]} )
		self.allFriends.insert( {"friend2" : id, "friend1" : friend["id"]} )

		if self.friendRequests.find_one( {"from": id, "to": friend["id"]} ) != None:
			self.friendRequests.remove( {"from": id, "to": friend["id"]} )
		if self.friendRequests.find_one( {"to": id, "from": friend["id"]} ) != None:
			self.friendRequests.remove( {"to": id, "from": friend["id"]} )

	def rejectFriend(self, id, friendEmail):
		friend = self.findUserByEmail(friendEmail)
		if (friend == None):
			raise FriendNotFoundException

		if self.friendRequests.find_one( {"from": id, "to": friend["id"]} ) != None:
			self.friendRequests.remove( {"from": id, "to": friend["id"]} )
		if self.friendRequests.find_one( {"to": id, "from": friend["id"]} ) != None:
			self.friendRequests.remove( {"to": id, "from": friend["id"]} )

	def deleteFriend(self, id, friendEmail):
		friend = self.findUserByEmail(friendEmail)
		if (friend == None):
			raise FriendNotFoundException

		self.allFriends.remove( {"friend1" : id, "friend2" : friend["id"]} )
		self.allFriends.remove( {"friend2" : id, "friend1" : friend["id"]} )



class FriendNotFoundException(Exception):
	def __init__(self):
		pass

class AuthException(Exception):
	def __init__(self):
		pass
