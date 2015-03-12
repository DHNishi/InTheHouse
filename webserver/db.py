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

		self.users.update( {'id':id}, {'$set': {'id':id, 'email': email, 'name': name, 'checkin': now} }, True )

	def getFriends(self, id):
		user = self.users.find_one( {'id':id} )
		friends = self.allFriends.find( {'friend1' : id} )
		result = []

		now = int(time.time())
		for pair in self.allFriends.find( {'friend1':user['id']} ):
			friend = self.findUserById(pair['friend2'])
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
		if (friend == None || friend['id'] == id):
			raise FriendNotFoundException

		#if not already friends
		if self.allFriends.find_one( {'friend1' : id, 'friend2' : friend['id']} ) == None:
			#if friend request doesn't already exist
			if self.friendRequests.find_one( {"from": id, "to": friend["id"]} ) == None:
				self.friendRequests.insert( {"from": id, "to": friend["id"]} )

	def getRequests(self, id):
		requests = self.friendRequests.find( {"to": id} )
		result = []
		for request in requests:
			friend = self.findUserById(request['from'])
			del friend['_id']
			result.append(friend)
		return result

	def acceptFriend(self, id, friendId):
		if self.findUserById(friendId) == None:
			raise FriendNotFoundException

		#add friendship
		self.allFriends.insert( {"friend1" : id, "friend2" : friendId} )
		self.allFriends.insert( {"friend2" : id, "friend1" : friendId} )

		#remove friend requests
		if self.friendRequests.find_one( {"from": id, "to": friendId} ) != None:
			self.friendRequests.remove( {"from": id, "to": friendId} )
		if self.friendRequests.find_one( {"to": id, "from": friendId} ) != None:
			self.friendRequests.remove( {"to": id, "from": friendId} )

	#Only for use in debugging/testing.
	def forceAcceptFriend(self, myEmail, friendEmail):
		me = self.findUserByEmail(myEmail)
		if me:
			id = me['id']
			print "***" + id
			self.acceptFriend(id, friendEmail)

	def rejectFriend(self, id, friendId):
		if self.findUserById(friendId) == None:
			raise FriendNotFoundException

		#remove friend requests
		if self.friendRequests.find_one( {"from": id, "to": friendId} ) != None:
			self.friendRequests.remove( {"from": id, "to": friendId} )
		if self.friendRequests.find_one( {"to": id, "from": friendId} ) != None:
			self.friendRequests.remove( {"to": id, "from": friendId} )

	def deleteFriend(self, id, friendId):
		if self.findUserById(friendId) == None:
			raise FriendNotFoundException

		#remove friendship
		self.allFriends.remove( {"friend1" : id, "friend2" : friendId} )
		self.allFriends.remove( {"friend2" : id, "friend1" : friendId} )


class FriendNotFoundException(Exception):
	def __init__(self):
		pass
