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
        """ Update given domains """
        self.collection.update_one({"domain": domain}, {"$pushAll": {"subdomains": newsubdomains}})

    def _findOne(self, domain):
        """ Retrun all subdomains for given domain """
        return self.collection.find_one({"domain": domain})

    def _delete(self, domain):
        """ Delete domains and subdomians for given domain """
        self.collection.find_one_and_delete({"domain": domain})
