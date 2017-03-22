# 
# 

from pymongo import MongoClient

DB_URL = 'mongodb://{dbuser}:{dbpassword}@ds135790.mlab.com:35790/maindb'

class db():
	def __init__(self, user, password, collection):
		self.client = MongoClient(DB_URL.format(dbuser=user, dbpassword=password))

		self.db = self.client['maindb']
		self.db.authenticate(user, password)
		print self.db
		self.collection = self.db[collection]
		print "[DB] CONNECTION SUCCESSFULL"

	def insert_document(self, post):
		self.collection.insert_one(post)
		print "[DB] DOCUMENT INSERTED"

	def get_document(self, key=None):
		return self.collection.find_one(key)

	def find_documents(self, key=None):
		return self.collection.find(key)

	def update_post(self, key, field_key, field_value):
		self.collection.update_one(
			key,
			{
			'$set': {
				field_key:field_value
			}
			}
		)
		print "[DB] DOCUMENT UPDATED"

	def delete_documents(self, key):
		self.collection.delete_many(key)
		print "[DB] DOCUMENTS DELETED"


