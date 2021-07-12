from pymongo import MongoClient
from config import dbHost, dbPort, dbName, collection



class ConfigDB:
    client = MongoClient(dbHost, dbPort, serverSelectionTimeoutMS=3000)
    db = client[dbName]
    collection = db[collection]

    def _findAll(self):
        """ Return all subdomains """
        return self.collection.find()

    def _add(self, target):
        """ Add new Domain to Database """
        self.collection.insert_one(target)

    def _update(self, domain, newsubdomains):
        """ Update subdomains for a given domain """
        for subdomain in newsubdomains: self.collection.update({"domain": domain}, {"$push": {"subdomains": subdomain}})

    def _findOne(self, domain):
        """ Retrun all subdomains for a given domain """
        return self.collection.find_one({"domain": domain})

    def _delete(self, domain):
        """ Delete domains and subdomians for a given domain """
        self.collection.find_one_and_delete({"domain": domain})
