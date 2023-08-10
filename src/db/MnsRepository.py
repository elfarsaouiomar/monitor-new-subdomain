from pymongo import MongoClient
from src.config.Config import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PWD, COLLECTION_NAME


class MnsRepository:
	client = MongoClient(host=DB_HOST,
	                     port=DB_PORT,
	                     username=DB_USER,
	                     password=DB_PWD,
	                     serverSelectionTimeoutMS=3000)
	
	db = client[DB_NAME]
	collection = db[COLLECTION_NAME]
	
	def find_all(self):
		""" Return all domains """
		return self.collection.find()
	
	def find_one(self, domain):
		""" Return a list of subdomains """
		return self.collection.find_one({"domain": domain})
	
	def add_domain(self, target):
		""" Add new Domain to Database """
		self.collection.insert_one(target)
	
	def update_domain(self, domain, newsubdomains):
		""" Update subdomains """
		for subdomain in newsubdomains: self.collection.update({"domain": domain}, {"$push": {"subdomains": subdomain}})
	
	def delete_domain(self, domain):
		""" Delete domain """
		self.collection.find_one_and_delete({"domain": domain})
