import pymongo

class DbInstance(object):
	client = None
	db = None

	def connect(self, host, uname, paswd):
		super(DbInstance, self).__init__()
		self.client = pymongo.MongoClient(host)
		self.db = self.client["data"]
		if not self.db.authenticate(uname, paswd):
			print "Auth error."
			raise Exception("Auth exception")

	def __init__(self, host, uname, paswd, waitTime):
		self.connect(host, uname, paswd)