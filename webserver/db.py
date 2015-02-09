import pymongo
import time

class DbInstance(object):
	client = None
	db = None
	users = None

	def connect(self, host, uname, paswd):
		super(DbInstance, self).__init__()
		self.client = pymongo.MongoClient(host)
		self.db = self.client["inthehouse"]
		self.users = self.db["users"]
		if not self.db.authenticate(uname, paswd):
			print "Auth error."
			raise Exception("Auth exception")

	def __init__(self, host, uname, paswd, waitTime):
		self.connect(host, uname, paswd)

	def checkin(self, id, email):
		now = str(int(time.time()))
		result = self.users.find_one( {'id': id} )
		if result == None:
			self.users.insert( {'id':id, 'email': email, 'checkin': now, 'friends':[]} )
		else:
			self.users.update( {'id':id}, {'$set': {'checkin':now} } )
